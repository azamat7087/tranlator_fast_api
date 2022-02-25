from sqlalchemy.sql.elements import or_
from core.utils import get_db

from core.db import Base
from pydantic import BaseModel
from fastapi import Query, Depends, Request, HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session, exc
from sqlalchemy import exc as sql_exc
import sys
import math


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)


def ordering_parameters(ordering: Optional[str] = Query("id")):
    return {"ordering": ordering}


def pagination_parameters(page: Optional[int] = Query(1, ge=1),
                          page_size: Optional[int] = Query(10, ge=1, le=1000)):
    return {"page": page, "page_size": page_size}


def search_parameters(search: Optional[str] = Query(None, max_length=100)):
    return {'search': search}


def default_parameters(request: Request, db: Session = Depends(get_db), ):
    return {'request': request, 'db': db}


def default_list_parameters(default_params: dict = Depends(default_parameters),
                            ordering: dict = Depends(ordering_parameters),
                            page: dict = Depends(pagination_parameters),
                            search: dict = Depends(search_parameters)):

    return {'default_params': default_params, "ordering": ordering, "page": page, "search": search}


class MixinBase:
    params = None
    db = None
    model = None
    page = None
    page_size = None
    reverse = None
    query = None
    count = None
    count_of_pages = None
    ordering = None
    search = None
    search_fields = None
    filtering = None


class ManyToManyMixin:
    db = None
    model = None

    async def clear_m2m(self, relation_table, item):
        for obj in self.db.query(relation_table).filter(getattr(relation_table, list(item.keys())[0]) == list(item.values())[0]).all():

            self.db.delete(obj)
            self.db.commit()

    async def set_m2m(self, item: dict, relation_items: dict, relation_table: Base):
        m2m_rows = []

        if relation_items.values():
            for relation_item in relation_items.values():
                for relation_item_id in relation_item:
                    m2m_item = {list(relation_items.keys())[0]: relation_item_id}
                    m2m_rows.append(relation_table(**item, **m2m_item))
            self.db.add_all(m2m_rows)
            self.db.commit()

        return await DetailMixin(db=self.db, model=self.model, query_value=["id", list(item.values())[0]]).get_detail()


class PaginatorMixin(MixinBase):

    def validate(self):
        if self.page > self.count_of_pages:
            raise Exception(f"Page is too large. Max page {self.count_of_pages}")

        if self.count_of_pages == 1:
            raise Exception("There is only 1 page")

    def get_page(self):
        try:
            self.validate()
            if not self.page == self.count_of_pages:
                right = self.page * self.page_size
                left = right - self.page_size
            else:
                right = self.count
                left = (self.page - 1) * self.page_size

            return self.query.slice(left, right).all()

        except Exception as e:
            if str(e) == f"Page is too large. Max page {self.count_of_pages}":
                return []
            elif str(e) == "There is only 1 page":
                return self.query.all()

    def paginate(self, query):
        self.query = query
        self.count = len(query.all())
        self.count_of_pages = math.ceil(self.count / self.page_size)

        page = self.get_page()
        count = self.count
        count_of_pages = self.count_of_pages
        return {"results": page, "count": count, "count_of_pages": count_of_pages}


class FilterMixin(MixinBase):

    async def check_filtering(self):
        if not self.filtering:
            return True
        return all(not value for value in self.filtering.values())

    async def filter_list(self):
        return await self.db.query(self.model).filter_by(**self.filtering)


class OrderMixin(MixinBase):
    def set_meta_attributes(self):

        if "-" in self.ordering['ordering']:
            self.ordering = {'value': self.ordering['ordering'].replace("-", ""), 'type': 'desc'}
        else:
            self.ordering = {'value': self.ordering['ordering'], 'type': 'asc'}

    def order(self, query):
        return query.order_by(
                getattr(getattr(self.model, self.ordering['value']), self.ordering['type'])())


class SearchMixin(MixinBase):
    def search_objects(self, query):

        parameters = [getattr(self.model, f"{field}").ilike('%' + str(self.search) + '%') for
                      field in self.search_fields if getattr(self.model, f"{field}").type.python_type == str]

        return query.filter(or_(*parameters))


class ListMixin(OrderMixin, SearchMixin, FilterMixin, PaginatorMixin):
    model = None
    params = None

    def __init__(self, params: dict, model: Base):
        self.params = params
        self.db = params['params']['default_params']['db']
        self.model = model
        self.page = params['params']['page']['page']
        self.page_size = params['params']['page']['page_size']
        self.ordering = params['params']['ordering']
        self.search = params['params']['search']['search']
        self.search_fields = params['search_fields']
        self.filtering = params.get('filtering', None)  # filter
        # self.clear_params()
        self.set_meta_attributes()

    async def get_list(self):

        filtering = await self.check_filtering()

        if filtering:
            query = self.db.query(self.model)
        else:
            query = self.filter_list()

        if self.search:
            query = self.search_objects(query)

        query = self.order(query)

        if query:
            paginated = self.paginate(query)

            return {"count": paginated["count"],
                    "page": f"{self.page} / {paginated['count_of_pages']}",
                    "results": paginated["results"]}

        return None


class DetailMixin:
    def __init__(self, query_value: list, db: Session, model: Base):
        self.query_value = query_value
        self.db = db
        self.model = model

    async def get_detail(self):
        return self.db.query(self.model).filter(getattr(self.model, self.query_value[0]) == self.query_value[1]).first()

    async def get_or_404(self):
        obj = await self.get_detail()
        if not obj:
            raise HTTPException(detail="Not found", status_code=status.HTTP_404_NOT_FOUND)
        return obj


class CreateMixin(ManyToManyMixin):
    def __init__(self, db: Session, model: Base,):
        self.db = db
        self.model = model

    async def create_many_to_many(self, item: dict, relation_items: dict, relation_table: Base):
        return await self.set_m2m(item, relation_items, relation_table)

    async def create_object(self, item):
        obj = self.model(**item.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    async def check_uniq(self, attribute: str, value: str):
        q = self.db.query(self.model).filter(getattr(self.model, attribute) == value)
        return self.db.query(q.exists()).scalar()


class UpdateMixin(ManyToManyMixin):
    def __init__(self, db: Session, model: Base,):
        self.db = db
        self.model = model

    async def update_many_to_many(self, item: dict, relation_items: dict, relation_table: Base):
        await self.clear_m2m(relation_table=relation_table, item=item)
        obj = await self.set_m2m(item, relation_items, relation_table)
        return obj

    async def update(self, db_object: BaseModel, new_object: BaseModel):

        try:
            for attribute, value in vars(new_object).items():
                setattr(db_object, attribute, value) if value else None

            self.db.add(db_object)
            self.db.commit()
            self.db.refresh(db_object)

        except sql_exc.IntegrityError as e:
            raise HTTPException(detail="Wrong foreign key", status_code=400)

        return db_object


class DeleteMixin:
    def __init__(self,  db: Session, model: Base):
        self.db = db
        self.model = model

    async def delete_object(self, pk):
        try:
            obj = self.db.query(self.model).filter(self.model.id == pk).first()
            self.db.delete(obj)
            self.db.commit()
        except exc.UnmappedInstanceError:
            raise HTTPException(detail="Not found", status_code=404)
