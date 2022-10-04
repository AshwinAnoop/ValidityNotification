from unicodedata import category
from django.shortcuts import redirect, render
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Advertisement, Categories,DocType, Document,FileUploads, InAppAds,Notification,Wallet,NotifyAds, WalletBalance
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta
import stripe #to use stripe as payment gateway
from django.conf import settings
from django.core.mail import send_mail

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
            if user.last_name == 'emp':
                return redirect('empHome')
            elif user.last_name == 'business':
                return redirect('businessHome')
            else:
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
    #checking email delivery
    checkDate = datetime.now().date() + timedelta(days=1)
    awaiting_notify = Notification.objects.filter(notify_date__lte = checkDate,is_notified = False)
    for x in awaiting_notify:
        notify_id = x.id
        doc_id = x.doc_id
        docname = Document.objects.get(id=doc_id).doc_name
        doccat = Document.objects.get(id=doc_id).category
        docsubcat = Document.objects.get(id=doc_id).sub_category
        doctype =Document.objects.get(id=doc_id).doc_type
        docfeedback = Document.objects.get(id=doc_id).feedback
        docexpiry = Document.objects.get(id=doc_id).end_date

        ad_id1 = NotifyAds.objects.get(doc_id = doc_id).ad_id1
        ad_id2 = NotifyAds.objects.get(doc_id = doc_id).ad_id2
        ad_id3 = NotifyAds.objects.get(doc_id = doc_id).ad_id3

        if ad_id1 != 0:
            adobj1 = Advertisement.objects.get(id = ad_id1)
        else:
            adobj1 = None
        if ad_id2 != 0:
            adobj2 = Advertisement.objects.get(id = ad_id2)
        else:
            adobj2 = None
        if ad_id3 != 0:
            adobj3 = Advertisement.objects.get(id = ad_id3)
        else:
            adobj3 = None

        if adobj1 or adobj2 or adobj3:
            suggest_msg = '\n\n\nSmart Suggestions\n'
            if adobj1 is not None:
                suggest_msg += adobj1.ad_title+'\n'
                suggest_msg += adobj1.ad_link+'\n'
            if adobj2 is not None:
                suggest_msg += adobj2.ad_title+'\n'
                suggest_msg += adobj2.ad_link+'\n'
            if adobj3 is not None:
                suggest_msg += adobj3.ad_title+'\n'
                suggest_msg += adobj3.ad_link+'\n'

        subject = 'Validity Notification system - Validity Expiring on '+str(docexpiry)
        message = 'Hi, thank you for registering with docusafe , this is a remainder notification\n'
        message += 'Your Document named : '+docname+' under category '+doccat+'\n'
        message += 'sub category : '+docsubcat+'\n'
        message += 'Type of Document : '+doctype+'\n'
        message += 'Feedback : '+docfeedback+'\n'
        message += 'Valid till : '+str(docexpiry)+'\n'
        message += 'This Document has generated a alert notification\n\n\n'
        message += suggest_msg

        email_from = settings.EMAIL_HOST_USER
        recipient_list = ['ashwinka999@gmail.com', ]
        #send_mail( subject, message, email_from, recipient_list )




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

        newInappAd = InAppAds(doc_id=docu_id,category=category,sub_category=sub_category,doc_type=doc_type)
        newInappAd.save()
        newNotiAd = NotifyAds(doc_id=docu_id,category=category,sub_category=sub_category,doc_type=doc_type)
        newNotiAd.save()


        print("successfully saved")

        return redirect('viewDocs')
    else:
        categories = Categories.objects.all()
        docu_types = DocType.objects.all()
        return render(request,'addDocs.html',{'categories' : categories, 'docu_types' : docu_types})

@login_required
def viewDocs(request):
    userid = request.user.id
    doc_objs = Document.objects.filter(user_id=userid).order_by('-id')
    return render(request,'viewDocs.html',{'doc_objs':doc_objs})

@login_required
def showDetails(request):
    doc_id = request.GET.get('document')
    doc_objs = Document.objects.filter(id=doc_id)
    notify_objs = Notification.objects.filter(doc_id = doc_id)
    fileobj = FileUploads.objects.filter(docu_id = doc_id)
    ad_id1 = InAppAds.objects.get(doc_id = doc_id).ad_id1
    ad_id2 = InAppAds.objects.get(doc_id = doc_id).ad_id2
    ad_id3 = InAppAds.objects.get(doc_id = doc_id).ad_id3

    if ad_id1 != 0:
        adobj1 = Advertisement.objects.get(id = ad_id1)
    else:
        adobj1 = None
    if ad_id2 != 0:
        adobj2 = Advertisement.objects.get(id = ad_id2)
    else:
        adobj2 = None
    if ad_id3 != 0:
        adobj3 = Advertisement.objects.get(id = ad_id3)
    else:
        adobj3 = None

    print(adobj1)
    print(adobj2)

    return render(request,'showDetails.html',{'doc_objs':doc_objs,'notify_objs':notify_objs,'fileobj':fileobj, 'adobj1':adobj1, 'adobj2':adobj2, 'adobj3':adobj3})

@login_required
def expiringDocs(request):
    user_id = request.user.id
    today = datetime.now().date()
    weekdate = datetime.now().date() + timedelta(days=7)
    monthdate = datetime.now().date() + timedelta(days=30)
    sixmonth = datetime.now().date() + timedelta(days=183)

    weekobjs = Document.objects.filter(user_id=user_id,end_date__range=[today, weekdate]).order_by('end_date')
    monthobjs = Document.objects.filter(user_id=user_id,end_date__range=[weekdate, monthdate]).order_by('end_date')
    sixmobjs = Document.objects.filter(user_id=user_id,end_date__range=[monthdate, sixmonth]).order_by('end_date')
    oneyearobjs = Document.objects.filter(user_id=user_id,end_date__gte = sixmonth).order_by('end_date')
    return render(request,'expiringDocs.html',{'weekobjs':weekobjs,'monthobjs':monthobjs,'sixmobjs':sixmobjs,'oneyearobjs':oneyearobjs})


@login_required
def empHome(request):
    args = {}
    args['business_count'] = User.objects.filter(last_name='business').count()
    args['total_users'] = User.objects.all().count()
    args['total_ads'] = Advertisement.objects.all().count()
    args['inapp_slots'] = InAppAds.objects.all().count() * 3
    args['notify_slots'] = NotifyAds.objects.all().count() * 3
    return render(request,'empHome.html',{'args' : args})

@login_required
def addBusiness(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = username
        busi_type = request.POST['businessType']
        last_name = 'business'
        if User.objects.filter(username=username).exists():
            messages.info(request,'Username already taken')
            return redirect('addBusiness')
        elif User.objects.filter(email=email).exists():
            messages.info(request,'Email already taken')
            return redirect('addBusiness')
        else:
            user = User.objects.create_user(username=username,password=password,email=email,first_name=busi_type,last_name=last_name)
            user.save()
            print("user created")
            user_id = user.id
            time = datetime.now()
            first_transact = Wallet(user_id=user_id,amount=1000,transactdate=time)
            first_transact.save()
            updateBalance = WalletBalance(user_id=user_id,balance=1000)
            updateBalance.save()
            messages.info(request,'Business added Successfully')
            return redirect('addBusiness')

    else:
        return render(request,'addBusiness.html')

@login_required
def businessInfo(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email = email)
        except User.DoesNotExist:
            user = None
        if user is not None:
            user_id = user.id
            transactions = Wallet.objects.filter(user_id=user_id)

            args = {}

            balance = WalletBalance.objects.get(user_id=user_id).balance
            total_purchase = WalletBalance.objects.get(user_id=user_id).total_ads
            total_spend = WalletBalance.objects.get(user_id=user_id).total_spend
            Iad_count = Advertisement.objects.filter(user_id=user_id,ad_type='inapp').count()
            Nad_count = Advertisement.objects.filter(user_id=user_id,ad_type='notify').count()
            total_ads = Iad_count+Nad_count

            args['Iad_count'] = Iad_count
            args['Nad_count'] = Nad_count
            args['total_ads'] = total_ads
            args['balance'] = balance
            args['total_purchase'] = total_purchase
            args['total_spend'] = total_spend

            return render(request,'businessDetails.html',{'user' : user,'transactions' : transactions, 'args':args})
        else:
            messages.info(request,'No email match found')
            return redirect('businessInfo')
    else:
        return render(request,'businessInfo.html')


@login_required
def businessHome(request):
    args = {}
    user_id = request.user.id
    iad_count1 = InAppAds.objects.filter(ad_id1=0).count()
    iad_count2 = InAppAds.objects.filter(ad_id2=0).count()
    iad_count3 = InAppAds.objects.filter(ad_id3=0).count()
    nad_count1 = NotifyAds.objects.filter(ad_id1=0).count()
    nad_count2 = NotifyAds.objects.filter(ad_id2=0).count()
    nad_count3 = NotifyAds.objects.filter(ad_id3=0).count()

    openCount = iad_count1+iad_count2+iad_count3+nad_count1+nad_count2+nad_count3

    myIad_count = Advertisement.objects.filter(user_id=user_id,ad_type='inapp').count()
    myNad_count = Advertisement.objects.filter(user_id=user_id,ad_type='notify').count()
    total_ads = myIad_count+myNad_count

    user_id = request.user.id
    balance = WalletBalance.objects.get(user_id=user_id).balance
    total_purchase = WalletBalance.objects.get(user_id=user_id).total_ads
    total_spend = WalletBalance.objects.get(user_id=user_id).total_spend

    args['openCount'] = openCount
    args['Iad_count'] = myIad_count
    args['Nad_count'] = myNad_count
    args['total_ads'] = total_ads
    args['balance'] = balance
    args['total_purchase'] = total_purchase
    args['total_spend'] = total_spend


    return render(request,'businessHome.html',{'args' : args})

@login_required
def advertiseHome(request):
    return render(request,'advertiseHome.html')

@login_required
def addIad(request):
    if request.method == 'POST':
        userid = request.user.id
        ad_name = request.POST['ad_name']
        ad_title = request.POST['ad_title']
        ad_content = request.POST['ad_content']
        ad_link = request.POST['ad_link']
        newIad = Advertisement(user_id=userid,ad_name=ad_name,ad_title=ad_title,ad_content=ad_content,ad_link=ad_link,ad_type='inapp')
        newIad.save()
        messages.info(request,'Successfully created new ad')
        return redirect('addIad')
    else:
        return render(request,'addIad.html')

@login_required
def viewIad(request):
    user_id = request.user.id
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='inapp')
    return render(request,'viewIad.html',{'ads':ads})

@login_required
def addNad(request):
    if request.method == 'POST':
        userid = request.user.id
        ad_name = request.POST['ad_name']
        ad_title = request.POST['ad_title']
        ad_content = request.POST['ad_content']
        ad_link = request.POST['ad_link']
        newIad = Advertisement(user_id=userid,ad_name=ad_name,ad_title=ad_title,ad_content=ad_content,ad_link=ad_link,ad_type='notify')
        newIad.save()
        messages.info(request,'Successfully created new ad')
        return redirect('viewNad')
    else:
        return render(request,'addNad.html')

@login_required
def viewNad(request):
    user_id = request.user.id
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='notify')
    return render(request,'viewNad.html',{'ads':ads})

@login_required
def wallet(request):
    args = {}
    user_id = request.user.id
    balance = WalletBalance.objects.get(user_id=user_id).balance
    args['balance'] = balance
    transacts = Wallet.objects.filter(user_id=user_id).order_by('-id')
    return render(request,'wallet.html',{'args' : args,'transacts' : transacts})

@login_required
def addMoney(request):
    if request.method == 'POST':
        amountvar = request.POST['cash']
        request.session["paynow"]=amountvar
        return redirect('checkout')   
    else:
        return render(request,'addMoney.html')

@login_required
def checkout(request):
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amountvar = request.session['paynow']
        transactdate = datetime.now()
        stripe_total = int(amountvar) * 100
        userid = request.user.id
        currbalance = WalletBalance.objects.get(user_id=userid).balance

        token = request.POST['stripeToken']
        email = request.POST['stripeEmail']
        customer = stripe.Customer.create(email=email,source=token)
        charge = stripe.Charge.create(amount=stripe_total,currency="inr",customer=customer.id)


        newbalance = int(currbalance) + int(amountvar)

        editbalance = WalletBalance.objects.get(user_id=userid) 
        editbalance.balance = newbalance
        editbalance.save();
        addobj = Wallet(amount=amountvar,user_id=userid,transactdate=transactdate)
        addobj.save();
        request.session["walletbalance"]=newbalance

        messages.info(request,'Deposit successful')
        return redirect('wallet')   

    else:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        data_key = settings.STRIPE_PUBLISHABLE_KEY
        amountvar = request.session['paynow']
        stripe_total = int(amountvar) * 100
        return render(request,'checkout.html',{'data_key' : data_key, 'stripe_total' : stripe_total})

@login_required
def marketHome(request):
    return render(request,'marketHome.html')

@login_required
def iCategoryslots(request):

    user_id = request.user.id

    categoryOpen1_query = InAppAds.objects.filter(ad_id1=0).values_list('category',flat=True).distinct()
    categoryOpen1 = list(categoryOpen1_query)
    cobj1 = {}
    for x in categoryOpen1:
        cat_count = InAppAds.objects.filter(ad_id1=0,category=x).count()
        cobj1[x] = cat_count

    categoryOpen2_query = InAppAds.objects.filter(ad_id2=0).values_list('category',flat=True).distinct()
    categoryOpen2 = list(categoryOpen2_query)
    cobj2 = {}
    for x in categoryOpen2:
        cat_count = InAppAds.objects.filter(ad_id2=0,category=x).count()
        cobj2[x] = cat_count

    categoryOpen3_query = InAppAds.objects.filter(ad_id3=0).values_list('category',flat=True).distinct()
    categoryOpen3 = list(categoryOpen3_query)
    cobj3 = {}
    for x in categoryOpen3:
        cat_count = InAppAds.objects.filter(ad_id3=0,category=x).count()
        cobj3[x] = cat_count

    
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='inapp')

    return render(request,'iCategoryslots.html',{'cobj1' : cobj1,'cobj2' : cobj2,'cobj3' : cobj3,'ads' : ads})


@login_required
def iSCategoryslots(request):

    user_id = request.user.id

    categoryOpen1_query = InAppAds.objects.filter(ad_id1=0).values_list('sub_category',flat=True).distinct()
    categoryOpen1 = list(categoryOpen1_query)
    cobj1 = {}
    for x in categoryOpen1:
        cat_count = InAppAds.objects.filter(ad_id1=0,sub_category=x).count()
        cobj1[x] = cat_count

    categoryOpen2_query = InAppAds.objects.filter(ad_id2=0).values_list('sub_category',flat=True).distinct()
    categoryOpen2 = list(categoryOpen2_query)
    cobj2 = {}
    for x in categoryOpen2:
        cat_count = InAppAds.objects.filter(ad_id2=0,sub_category=x).count()
        cobj2[x] = cat_count

    categoryOpen3_query = InAppAds.objects.filter(ad_id3=0).values_list('sub_category',flat=True).distinct()
    categoryOpen3 = list(categoryOpen3_query)
    cobj3 = {}
    for x in categoryOpen3:
        cat_count = InAppAds.objects.filter(ad_id3=0,sub_category=x).count()
        cobj3[x] = cat_count

    
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='inapp')

    return render(request,'iSCategoryslots.html',{'cobj1' : cobj1,'cobj2' : cobj2,'cobj3' : cobj3,'ads' : ads})

@login_required
def iDCategoryslots(request):
    user_id = request.user.id

    categoryOpen1_query = InAppAds.objects.filter(ad_id1=0).values_list('doc_type',flat=True).distinct()
    categoryOpen1 = list(categoryOpen1_query)
    cobj1 = {}
    for x in categoryOpen1:
        cat_count = InAppAds.objects.filter(ad_id1=0,doc_type=x).count()
        cobj1[x] = cat_count

    categoryOpen2_query = InAppAds.objects.filter(ad_id2=0).values_list('doc_type',flat=True).distinct()
    categoryOpen2 = list(categoryOpen2_query)
    cobj2 = {}
    for x in categoryOpen2:
        cat_count = InAppAds.objects.filter(ad_id2=0,doc_type=x).count()
        cobj2[x] = cat_count

    categoryOpen3_query = InAppAds.objects.filter(ad_id3=0).values_list('doc_type',flat=True).distinct()
    categoryOpen3 = list(categoryOpen3_query)
    cobj3 = {}
    for x in categoryOpen3:
        cat_count = InAppAds.objects.filter(ad_id3=0,doc_type=x).count()
        cobj3[x] = cat_count

    
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='inapp')

    return render(request,'iDCategoryslots.html',{'cobj1' : cobj1,'cobj2' : cobj2,'cobj3' : cobj3,'ads' : ads})    

@login_required
def nCategoryslots(request):

    user_id = request.user.id

    categoryOpen1_query = NotifyAds.objects.filter(ad_id1=0).values_list('category',flat=True).distinct()
    categoryOpen1 = list(categoryOpen1_query)
    cobj1 = {}
    for x in categoryOpen1:
        cat_count = NotifyAds.objects.filter(ad_id1=0,category=x).count()
        cobj1[x] = cat_count

    categoryOpen2_query = NotifyAds.objects.filter(ad_id2=0).values_list('category',flat=True).distinct()
    categoryOpen2 = list(categoryOpen2_query)
    cobj2 = {}
    for x in categoryOpen2:
        cat_count = NotifyAds.objects.filter(ad_id2=0,category=x).count()
        cobj2[x] = cat_count

    categoryOpen3_query = NotifyAds.objects.filter(ad_id3=0).values_list('category',flat=True).distinct()
    categoryOpen3 = list(categoryOpen3_query)
    cobj3 = {}
    for x in categoryOpen3:
        cat_count = NotifyAds.objects.filter(ad_id3=0,category=x).count()
        cobj3[x] = cat_count

    
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='notify')

    return render(request,'nCategoryslots.html',{'cobj1' : cobj1,'cobj2' : cobj2,'cobj3' : cobj3,'ads' : ads})


@login_required
def nSCategoryslots(request):

    user_id = request.user.id

    categoryOpen1_query = NotifyAds.objects.filter(ad_id1=0).values_list('sub_category',flat=True).distinct()
    categoryOpen1 = list(categoryOpen1_query)
    cobj1 = {}
    for x in categoryOpen1:
        cat_count = NotifyAds.objects.filter(ad_id1=0,sub_category=x).count()
        cobj1[x] = cat_count

    categoryOpen2_query = NotifyAds.objects.filter(ad_id2=0).values_list('sub_category',flat=True).distinct()
    categoryOpen2 = list(categoryOpen2_query)
    cobj2 = {}
    for x in categoryOpen2:
        cat_count = NotifyAds.objects.filter(ad_id2=0,sub_category=x).count()
        cobj2[x] = cat_count

    categoryOpen3_query = NotifyAds.objects.filter(ad_id3=0).values_list('sub_category',flat=True).distinct()
    categoryOpen3 = list(categoryOpen3_query)
    cobj3 = {}
    for x in categoryOpen3:
        cat_count = NotifyAds.objects.filter(ad_id3=0,sub_category=x).count()
        cobj3[x] = cat_count

    
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='notify')

    return render(request,'nSCategoryslots.html',{'cobj1' : cobj1,'cobj2' : cobj2,'cobj3' : cobj3,'ads' : ads})


@login_required
def nDCategoryslots(request):

    user_id = request.user.id

    categoryOpen1_query = NotifyAds.objects.filter(ad_id1=0).values_list('doc_type',flat=True).distinct()
    categoryOpen1 = list(categoryOpen1_query)
    cobj1 = {}
    for x in categoryOpen1:
        cat_count = NotifyAds.objects.filter(ad_id1=0,doc_type=x).count()
        cobj1[x] = cat_count

    categoryOpen2_query = NotifyAds.objects.filter(ad_id2=0).values_list('doc_type',flat=True).distinct()
    categoryOpen2 = list(categoryOpen2_query)
    cobj2 = {}
    for x in categoryOpen2:
        cat_count = NotifyAds.objects.filter(ad_id2=0,doc_type=x).count()
        cobj2[x] = cat_count

    categoryOpen3_query = NotifyAds.objects.filter(ad_id3=0).values_list('doc_type',flat=True).distinct()
    categoryOpen3 = list(categoryOpen3_query)
    cobj3 = {}
    for x in categoryOpen3:
        cat_count = NotifyAds.objects.filter(ad_id3=0,doc_type=x).count()
        cobj3[x] = cat_count

    
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='notify')

    return render(request,'nDCategoryslots.html',{'cobj1' : cobj1,'cobj2' : cobj2,'cobj3' : cobj3,'ads' : ads})

@login_required
def purchaseICslot1(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id1=0,category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iCategoryslots')
    elif currbalance < (slots*3):
        messages.info(request,'Balance too low')
        return redirect('iCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id1=0,category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 3)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*3)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*3
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id1 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iCategoryslots')



@login_required
def purchaseICslot2(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id2=0,category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iCategoryslots')
    elif currbalance < (slots*2):
        messages.info(request,'Balance too low')
        return redirect('iCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id2=0,category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 2)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*2)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*2
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id2 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iCategoryslots')

@login_required
def purchaseICslot3(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id3=0,category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iCategoryslots')
    elif currbalance < slots:
        messages.info(request,'Balance too low')
        return redirect('iCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id3=0,category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + slots
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - slots
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots
        total_ads = curr_purchase+n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id3 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iCategoryslots')


@login_required
def purchaseISCslot1(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    sub_category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id1=0,sub_category=sub_category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iSCategoryslots')
    elif currbalance < (slots*3):
        messages.info(request,'Balance too low')
        return redirect('iSCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id1=0,sub_category=sub_category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 3)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*3)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*3
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id1 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iSCategoryslots')


@login_required
def purchaseISCslot2(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    sub_category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id2=0,sub_category=sub_category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iSCategoryslots')
    elif currbalance < (slots*2):
        messages.info(request,'Balance too low')
        return redirect('iSCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id2=0,sub_category=sub_category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 2)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*2)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*2
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id2 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iSCategoryslots')

@login_required
def purchaseISCslot3(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    sub_category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id3=0,sub_category=sub_category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iSCategoryslots')
    elif currbalance < slots:
        messages.info(request,'Balance too low')
        return redirect('iSCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id3=0,sub_category=sub_category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + slots
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - slots
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots
        total_ads = curr_purchase+n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id3 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iSCategoryslots')


@login_required
def purchaseIDCslot1(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    doc_type = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id1=0,doc_type=doc_type).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iDCategoryslots')
    elif currbalance < (slots*3):
        messages.info(request,'Balance too low')
        return redirect('iDCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id1=0,doc_type=doc_type)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 3)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*3)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*3
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id1 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iDCategoryslots')

@login_required
def purchaseIDCslot2(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    doc_type = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id2=0,doc_type=doc_type).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iDCategoryslots')
    elif currbalance < (slots*2):
        messages.info(request,'Balance too low')
        return redirect('iDCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id2=0,doc_type=doc_type)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 2)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*2)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*2
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id2 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iDCategoryslots')


@login_required
def purchaseIDCslot3(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    doc_type = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = InAppAds.objects.filter(ad_id3=0,doc_type=doc_type).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('iDCategoryslots')
    elif currbalance < slots:
        messages.info(request,'Balance too low')
        return redirect('iDCategoryslots')
    else:
        adobjs = InAppAds.objects.filter(ad_id3=0,doc_type=doc_type)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + slots
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - slots
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots
        total_ads = curr_purchase+n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id3 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('iDCategoryslots')



@login_required
def purchases(request):
    user_id = request.user.id
    purchaseobjs = Advertisement.objects.filter(user_id=user_id).order_by('-publish_count')
    return render(request,'purchases.html',{'purchaseobjs' : purchaseobjs})

@login_required
def businessReport(request):
    user_id = request.user.id
    purchaseobjs = Advertisement.objects.filter(user_id=user_id).order_by('-publish_count')
    expendobjs = Advertisement.objects.filter(user_id=user_id).order_by('-amount_spend')
    inappobjs = Advertisement.objects.filter(user_id=user_id,ad_type='inapp').order_by('-publish_count')
    emailobjs = Advertisement.objects.filter(user_id=user_id,ad_type='notify').order_by('-publish_count')

    all_ads = list(Advertisement.objects.filter(user_id=user_id).values_list('id',flat=True))
    allcats = list(InAppAds.objects.filter(ad_id1__in = all_ads).values_list('category',flat=True).distinct() | InAppAds.objects.filter(ad_id2__in = all_ads).values_list('category',flat=True).distinct() | InAppAds.objects.filter(ad_id3__in = all_ads).values_list('category',flat=True).distinct())

    cat_reportobjs = {}

    for cat in allcats:
        scount1 = InAppAds.objects.filter(category=cat,ad_id1__in = all_ads).count()
        scount2 = InAppAds.objects.filter(category=cat,ad_id2__in = all_ads).count()
        scount3 = InAppAds.objects.filter(category=cat,ad_id3__in = all_ads).count()
        totalslots = scount1+scount2+scount3
        arr = [scount1,scount2,scount3,totalslots]
        cat_reportobjs[cat] = arr
    
    allsubcats = list(InAppAds.objects.filter(ad_id1__in = all_ads).values_list('sub_category',flat=True).distinct() | InAppAds.objects.filter(ad_id2__in = all_ads).values_list('sub_category',flat=True).distinct() | InAppAds.objects.filter(ad_id3__in = all_ads).values_list('sub_category',flat=True).distinct())
    
    subcat_reportobjs = {}

    for subcat in allsubcats:
        scount1 = InAppAds.objects.filter(sub_category=subcat,ad_id1__in = all_ads).count()
        scount2 = InAppAds.objects.filter(sub_category=subcat,ad_id2__in = all_ads).count()
        scount3 = InAppAds.objects.filter(sub_category=subcat,ad_id3__in = all_ads).count()
        totalslots = scount1+scount2+scount3
        arr = [scount1,scount2,scount3,totalslots]
        subcat_reportobjs[subcat] = arr



    context = {
        'purchaseobjs' : purchaseobjs,
        'expendobjs' : expendobjs,
        'inappobjs' : inappobjs,
        'emailobjs' : emailobjs,
        'cat_reportobjs' : cat_reportobjs,
        'subcat_reportobjs' : subcat_reportobjs,
    }
    return render(request,'businessReport.html',context)

@login_required
def businessManual(request):
    return render(request,'businessManual.html')



@login_required
def purchaseNCslot1(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id1=0,category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nCategoryslots')
    elif currbalance < (slots*3):
        messages.info(request,'Balance too low')
        return redirect('nCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id1=0,category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 3)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*3)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*3
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id1 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nCategoryslots')


@login_required
def purchaseNCslot2(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id2=0,category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nCategoryslots')
    elif currbalance < (slots*2):
        messages.info(request,'Balance too low')
        return redirect('nCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id2=0,category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 2)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*2)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*2
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id2 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nCategoryslots')


@login_required
def purchaseNCslot3(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id3=0,category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nCategoryslots')
    elif currbalance < slots:
        messages.info(request,'Balance too low')
        return redirect('nCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id3=0,category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + slots 
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - slots
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id3 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nCategoryslots')

@login_required
def purchaseNSCslot1(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id1=0,sub_category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nSCategoryslots')
    elif currbalance < (slots*3):
        messages.info(request,'Balance too low')
        return redirect('nSCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id1=0,sub_category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 3)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*3)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*3
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id1 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nSCategoryslots')


@login_required
def purchaseNSCslot2(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id2=0,sub_category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nSCategoryslots')
    elif currbalance < (slots*2):
        messages.info(request,'Balance too low')
        return redirect('nSCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id2=0,sub_category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 2)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*2)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*2
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id2 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nSCategoryslots')



@login_required
def purchaseNSCslot3(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id3=0,sub_category=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nSCategoryslots')
    elif currbalance < slots:
        messages.info(request,'Balance too low')
        return redirect('nSCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id3=0,sub_category=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + slots 
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - slots
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id3 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nSCategoryslots')



@login_required
def purchaseNDCslot1(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id1=0,doc_type=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nDCategoryslots')
    elif currbalance < (slots*3):
        messages.info(request,'Balance too low')
        return redirect('nDCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id1=0,doc_type=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 3)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*3)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*3
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id1 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nDCategoryslots')




@login_required
def purchaseNDCslot2(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id2=0,doc_type=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nDCategoryslots')
    elif currbalance < (slots*2):
        messages.info(request,'Balance too low')
        return redirect('nDCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id2=0,doc_type=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + (slots * 2)
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - (slots*2)
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots*2
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id2 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nDCategoryslots')



@login_required
def purchaseNDCslot3(request):
    user_id = request.user.id
    ad_id = request.POST['ad']
    category = request.POST['category']
    slots = int(request.POST['noofslots'])
    cat_count = NotifyAds.objects.filter(ad_id3=0,doc_type=category).count()
    currbalance = WalletBalance.objects.get(user_id=user_id).balance
    if cat_count < slots:
        messages.info(request,'No Enough Slots available')
        return redirect('nDCategoryslots')
    elif currbalance < slots:
        messages.info(request,'Balance too low')
        return redirect('nDCategoryslots')
    else:
        adobjs = NotifyAds.objects.filter(ad_id3=0,doc_type=category)
        ad_details = Advertisement.objects.get(id=ad_id)
        curr_adcount = ad_details.publish_count
        curr_adspend = ad_details.amount_spend
        newspend = curr_adspend + slots 
        ad_details.amount_spend = newspend
        newadcount = curr_adcount + slots
        ad_details.publish_count = newadcount
        newbalance = currbalance - slots
        curr_data = WalletBalance.objects.get(user_id=user_id)
        curr_purchase = curr_data.total_ads
        curr_spend = curr_data.total_spend
        n_purchases = slots
        n_spend = slots
        total_ads = curr_purchase + n_purchases
        total_spend = curr_spend + n_spend
        loopcount = 0
        for ad in adobjs:
            ad.ad_id3 = ad_id
            ad.save()
            loopcount+=1
            if loopcount == slots:
                break
        
        curr_data.balance = newbalance
        curr_data.total_ads = total_ads
        curr_data.total_spend = total_spend
        curr_data.save()
        ad_details.save()
        print("slots purchased")
        messages.info(request,'slots purchased')
        return redirect('nDCategoryslots')

@login_required
def addNotification(request):
    if request.method == 'POST':
        doc_id = request.POST['doc_id']
        notify_date = request.POST['notifydate']
        newnoti = Notification(doc_id=doc_id,notify_date=notify_date)
        newnoti.save()
        messages.info(request,'Notification Added')
        return redirect('viewDocs')
    else:
        doc_id = request.GET.get('document')
        return render(request,'addNotification.html',{'doc_id' : doc_id})

@login_required
def upcomingNotification(request):
    user_id = request.user.id
    docobj = {}
    userdocs = Document.objects.filter(user_id=user_id)
    docids = list(Document.objects.filter(user_id=user_id).values_list('id',flat=True))
    for eachdoc in userdocs:
        docid = eachdoc.id
        docobj[docid] = eachdoc.doc_name
    
    notifyobjs = Notification.objects.filter(doc_id__in = docids).order_by('notify_date')

    notifies = []

    for noti in notifyobjs:
        doc_id = noti.doc_id
        arrobj = {}
        arrobj[docobj[doc_id]] = noti.notify_date
        notifies.append(arrobj)
    
    
    return render(request,'upcomingNotification.html',{'notifies' : notifies})
