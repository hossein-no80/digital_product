from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Product, Category, File
from .serializers import ProductSerializer, CategorySerializer, FileSerializer


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True, context={'request': request})
        return Response(serializer.data)


class CategoryDetailView(APIView):
    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            raise Http404

        serializer = CategorySerializer(category, context={'request': request})
        return Response(serializer.data)


class ProductListView(APIView):

    def get(self, request):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ProductDetailView(APIView):
    def get(self, request, pk):
        try:
            products = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

        serializer = ProductSerializer(products, context={'request': request})
        return Response(serializer.data)


class FileListView(APIView):
    def get(self, request, product_id):
        file = File.objects.filter(product_id=product_id)
        serializer = FileSerializer(file, many=True, context={'request': request})
        return Response(serializer.data)


class FileDetailView(APIView):
    def get(self, request, pk, product_id):
        try:
            file = File.objects.get(pk=pk, product_id=product_id)
        except File.DoesNotExist:
            raise Http404
        serializer = FileSerializer(file, context={'request': request})
        return Response(serializer.data)
