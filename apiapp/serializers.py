
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from apiapp.models import *




class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BooksBook
        fields = ('__all__')