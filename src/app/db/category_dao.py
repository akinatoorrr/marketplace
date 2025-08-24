from .base_dao import BlogDAO
from .models import Category


class CategoryDAO(BlogDAO[Category]):
    model = Category
