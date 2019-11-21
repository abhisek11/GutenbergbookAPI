from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from django.conf import settings
from rest_framework import filters
from apiapp.models import *
from apiapp.serializers import *
from custom_decorator import *
from pagination import CSPageNumberPagination

# Create your views here.

class BookListView(generics.ListAPIView):
    pagination_class = CSPageNumberPagination
    queryset = BooksBook.objects.order_by('-id')
    serializer_class = BookListSerializer

    def get_queryset(self):
        filter={}
        book_id=self.request.query_params.get('book_id', None)
        language=self.request.query_params.get('language', None)
        mime_type=self.request.query_params.get('mime_type', None)
        topic=self.request.query_params.get('topic', None)
        author=self.request.query_params.get('author', None)
        # if author:
        #     name = BooksAuthor.objects.filter(name=author)

        #     for na in name:
        #         book_id=BooksBookAuthors.objects.filter(author_id=na.id).values('book_id')
        #         print("book_id",book_id)
        #     book_id_list = [x['book_id'] for x in book_id]
        #     print(book_id_list)
        #     filter['id__in']=book_id_list
        #     print(filter)
        if book_id:
            # gutenberg_id = BooksBook.objects.get(gutenberg_id=book_id).id
            filter['id']= book_id
        if language:
            lang_id_list=[]
            language_data=language.split(',')
            # print("language_data",language_data)
            language_id = BooksLanguage.objects.filter(code__in=language_data)
            for lang in language_id:
                book_lang = BooksBookLanguages.objects.filter(language_id=lang.id)
                for x in book_lang:
                    lang_id_list.append(x.book_id)

            filter['id__in']= lang_id_list
        if mime_type:
            mime_type_id_list=[]
            mime_type=mime_type.split(',')
            for m_type in mime_type:
                mime_type_id = BooksFormat.objects.filter(mime_type=m_type).values('book_id').distinct()
                # final_query = mime_type_id.distinct('book_id')
                print(mime_type_id.query)
                for mime in mime_type_id:
                    mime_type_id_list.append(mime['book_id'])
            print(len(mime_type_id_list))
            filter['id__in']= mime_type_id_list
        if topic:
            top1_list=[]
            top2_list=[]
            top=topic.split(',')
            for topic in top:
                topic_data1 = BooksSubject.objects.filter(name__icontains =topic)
                print(topic_data1.query)
                for top1 in topic_data1:
                    shelv_topic = BooksBookBookshelves.objects.filter(bookshelf_id=top1.id)
                    for s_t in shelv_topic:
                        top1_list.append(s_t.book_id)

                topic_data2 = BooksBookshelf.objects.filter(name__icontains =topic)
                print(topic_data2.query)
                for top2 in topic_data2:
                    subject_topic = BooksBookSubjects.objects.filter(subject_id=top2.id)
                    for s_t in subject_topic:
                        top2_list.append(s_t.book_id)

            book_id = list(set(top1_list+top2_list))
            # print('book_id',book_id)
            filter['id__in'] = book_id

            

            
        if filter:
            queryset = self.queryset.filter(**filter)
            # print('queryset',queryset)
            return queryset

        else:
            return self.queryset


    # @response_modify_decorator_list_after_execution
    def get(self,request,*args,**kwargs):
        response = super(BookListView,self).get(self,request,args,kwargs)
        # mime_type=self.request.query_params.get('mime_type', None)
        # mime_type_list=mime_type.split(',')
        for data in response.data['results']:
            # print(data['id'])
            book_auther = BooksBookAuthors.objects.filter(book_id=data['id'])
            # print(book_auther)
            if book_auther:
                for x in book_auther:
                    author_information = BooksAuthor.objects.filter(id=x.author_id).\
                        values('id','birth_year','death_year','name')
            else:
                author_information=[]
            book_shelves_id = BooksBookBookshelves.objects.filter(book_id=data['id'])
            book_shelves_details = [BooksBookshelf.objects.filter(id=str(b_s.bookshelf_id)).values('name')[0] for b_s in book_shelves_id]
            book_subject_id = BooksBookSubjects.objects.filter(book_id=data['id'])
            book_subject_details = [BooksSubject.objects.filter(id=str(b_s.subject_id)).values('name')[0] for b_s in book_subject_id]
            book_language_id = BooksBookLanguages.objects.filter(book_id=data['id'])
            if book_language_id:
                for x in book_language_id:
                    book_language_details = BooksLanguage.objects.filter(id=str(x.language_id)).values('code')
            else:
                book_language_details=None
            book_format_details = BooksFormat.objects.filter(book_id=data['id']).values('mime_type','url')
            data['title'] = data['title']
            data['author_information']=author_information[0] if author_information else author_information
            data['book_shelves']=book_shelves_details
            data['book_subject']=book_subject_details
            data['book_language']=book_language_details[0]['code'] if book_language_details else book_language_details
            data['book_format_details']=book_format_details[0] if book_format_details else []


        return response
