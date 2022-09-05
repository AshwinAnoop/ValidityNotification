from tracemalloc import start
from unicodedata import category
from django.shortcuts import redirect, render
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Categories,DocType, Document,FileUploads,Notification
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return redirect('/home')
    else:
        return render(request,'index.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password'] 

        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request,user)
            return redirect('home')
        else:
            messages.info(request,'Invalid Credentials')
            return render(request,'login.html')

    else:
        return render(request,'login.html')

def register(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmpassword = request.POST['confirmpassword']

        if password == confirmpassword:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username already taken')
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email already taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username,password=password,email=email)
                user.save()
                print("user created")
        else:
            messages.info(request,'password not matching')
            return redirect('register')
    else:
        return render(request,'register.html')
    return redirect('/')

@login_required
def home(request):
    return render(request,'home.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

@login_required
def addDocs(request):
    #file upload not done
    if request.method == 'POST':
        userid = request.user.id
        docname = request.POST['docname']
        category_id = request.POST['category']
        doctype_id = request.POST['doctype']
        startdate = request.POST['startdate']
        enddate = request.POST['enddate']
        feedback = request.POST['feedback']
        uploadfile = request.FILES['uploadfiles']
        if 'oneday-before' in request.POST:
            oneday_before = request.POST['oneday-before']
        else:
            oneday_before = False
        if 'oneweek-before' in request.POST:
            oneweek_before = request.POST['oneweek-before']
        else:
            oneweek_before = False
        if 'onemonth-before' in request.POST:
            onemonth_before = request.POST['onemonth-before']
        else:
            onemonth_before = False
        
        cat_obj = Categories.objects.get(id=category_id)
        category = cat_obj.category
        sub_category = cat_obj.sub_category

        doct_obj = DocType.objects.get(id=doctype_id)
        doc_type = doct_obj.document_type

        newDoc = Document(user_id=userid,doc_name=docname,category=category,sub_category=sub_category,doc_type=doc_type,start_date=startdate,end_date=enddate,feedback=feedback,no_of_files=1,last_day=oneday_before,last_week=oneweek_before,last_month=onemonth_before)
        newDoc.save()

        docu_id = newDoc.id
        fss = FileSystemStorage()
        #file = fss.save(uploadfile.name, uploadfile)
        file = fss.save(str(docu_id)+".pdf", uploadfile)
        file_url = fss.url(file)
        newUpload = FileUploads(docu_id=docu_id,filepath=file_url)
        newUpload.save()

        if oneday_before:
            end_date = datetime.strptime(enddate, '%Y-%m-%d')
            end_date = end_date.date()
            notify1 = end_date - timedelta(hours=24)
            if notify1 > datetime.now().date():
                newNoti1 = Notification(doc_id=docu_id,notify_date=notify1)
                newNoti1.save()

        if oneweek_before:
            end_date = datetime.strptime(enddate, '%Y-%m-%d')
            end_date = end_date.date()
            notify2 = end_date - timedelta(hours=168)
            if notify2 > datetime.now().date():
                newNoti2 = Notification(doc_id=docu_id,notify_date=notify2)
                newNoti2.save()

        if onemonth_before:
            end_date = datetime.strptime(enddate, '%Y-%m-%d')
            end_date = end_date.date()
            notify3 = end_date - timedelta(hours=720)
            if notify3 > datetime.now().date():
                newNoti3 = Notification(doc_id=docu_id,notify_date=notify3)
                newNoti3.save()


        print("successfully saved")

        return redirect('viewDocs')
    else:
        categories = Categories.objects.all()
        docu_types = DocType.objects.all()
        return render(request,'addDocs.html',{'categories' : categories, 'docu_types' : docu_types})

@login_required
def viewDocs(request):
    userid = request.user.id
    doc_objs = Document.objects.filter(user_id=userid)
    return render(request,'viewDocs.html',{'doc_objs':doc_objs})