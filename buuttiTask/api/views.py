from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json
from api.models import Books

# Create your views here.
@csrf_exempt
def books(request): #handles all requests to /api/books
    try:
        if request.method == 'GET':
            if ("title" in request.GET and request.GET["title"] == "") or ("author" in request.GET and request.GET["author"] == "") or ("year" in request.GET and request.GET["year"] == "" and type(request.GET["year"]) != int): #checks if any of the parameters are empty
                return JsonResponse({"error": "Please provide a title, author, and year."}, status=400)
            if "author" in request.GET and "publisher" in request.GET and "year" in request.GET: #checks if all parameters are provided
                currentBooks = list(Books.objects.filter(author=request.GET["author"], year=request.GET["year"], publisher=request.GET["publisher"]).values())
            elif "author" in request.GET and "publisher" in request.GET: #checks if author and publisher are provided
                currentBooks = list(Books.objects.filter(author=request.GET["author"], publisher=["publisher"]).values())
            elif "author" in request.GET and "year" in request.GET: #checks if author and year are provided
                currentBooks = list(Books.objects.filter(year=request.GET["year"], author=["author"]).values())
            elif "publisher" in request.GET and "year" in request.GET: #checks if publisher and year are provided
                currentBooks = list(Books.objects.filter(publisher=request.GET["publisher"], year=request.GET["year"]).values())
            elif "author" in request.GET: #checks if author is provided
                currentBooks = list(Books.objects.filter(author=request.GET["author"]).values())
            elif "publisher" in request.GET: #checks if publisher is provided
                currentBooks = list(Books.objects.filter(publisher=request.GET["publisher"]).values())
            elif "year" in request.GET: #checks if year is provided
                currentBooks = list(Books.objects.filter(year=request.GET["year"]).values())
            else: #if no parameters are provided return all books
                currentBooks = list(Books.objects.all().values())
            return JsonResponse(currentBooks, safe=False)
        elif request.method == 'POST':
            try: #checks if the request body is valid json
                jsonBody = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON'}, status=400)
            if "title" in jsonBody and "author" in jsonBody and "year" in jsonBody and jsonBody["title"] and jsonBody["author"] and jsonBody["year"] and type(jsonBody["year"]) == int: #checks if all required fields are provided and are valid
                if "publisher" in jsonBody and jsonBody["publisher"] == "": #checks if publisher is empty
                    return JsonResponse({"error": "publisher cannot be empty"}, status=400)
                if doesBookExist(jsonBody): #checks if the book already exists
                    return JsonResponse({"error": "book already exists"}, status=400)
                if "publisher" in jsonBody and "description" in jsonBody: #checks if publisher and description are provided
                    book = Books(title=jsonBody["title"], author=jsonBody["author"], year=jsonBody["year"], publisher=jsonBody["publisher"], description=jsonBody["description"])
                elif "publisher" in jsonBody: #checks if publisher is provided
                    book = Books(title=jsonBody["title"], author=jsonBody["author"], year=jsonBody["year"], publisher=jsonBody["publisher"])
                elif "description" in jsonBody: #checks if description is provided
                    book = Books(title=jsonBody["title"], author=jsonBody["author"], year=jsonBody["year"], description=jsonBody["description"])
                else: #if no optional fields are provided
                    book = Books(title=jsonBody["title"], author=jsonBody["author"], year=jsonBody["year"])
                book.save() #saves the book to the database
                bookId = book.pk #gets the id of the book
                return JsonResponse({"id": bookId}, status=200) #returns the id of the book
            else:
                return JsonResponse({"error": "title, author, and year are required fields"}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Internal Server Error", "specific": e}, status=500)

def doesBookExist(jsonBody): #checks if a book already exists
    currentBooks = Books.objects.filter(title=jsonBody["title"], author=jsonBody["author"], year=jsonBody["year"]) #gets all books with the same title, author, and year
    if currentBooks: #if the book exists return true
        return True
    return False

@csrf_exempt
def singleBook(request, bookId): #handles requests for a single book
    try:
        if request.method == "GET":
            if not type(bookId) == int:
                return JsonResponse({"error": "Book not found"}, status=404)
            try:
                book = Books.objects.get(id=bookId)
                book = model_to_dict(book)
                return JsonResponse(book, safe=False)
            except Books.DoesNotExist:
                return JsonResponse({"error": "Book not found"}, status=404)
        elif request.method == "DELETE":
            if not type(bookId) == int:
                return JsonResponse({"error": "Book not found"}, status=404)
            try:
                book = Books.objects.get(id=bookId)
                book.delete()
                return JsonResponse({"message": "Book deleted successfully"}, status=204)
            except Books.DoesNotExist:
                return JsonResponse({"error": "Book not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": "Internal Server Error", "specific":e}, status=500)


