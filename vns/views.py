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

        newInappAd = InAppAds(doc_id=docu_id,category=category,sub_category=sub_category)
        newInappAd.save()
        newNotiAd = NotifyAds(doc_id=docu_id,category=category,sub_category=sub_category)
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
    doc_objs = Document.objects.filter(user_id=userid)
    return render(request,'viewDocs.html',{'doc_objs':doc_objs})

@login_required
def showDetails(request):
    doc_id = request.GET.get('document')
    doc_objs = Document.objects.filter(id=doc_id)
    notify_objs = Notification.objects.filter(doc_id = doc_id)
    fileobj = FileUploads.objects.filter(docu_id = doc_id)
    return render(request,'showDetails.html',{'doc_objs':doc_objs,'notify_objs':notify_objs,'fileobj':fileobj})

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
    return render(request,'empHome.html')

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
            return render(request,'businessDetails.html',{'user' : user,'transactions' : transactions})
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

    categoryOpen3_query = InAppAds.objects.filter(ad_id3=0).values_list('category',flat=True).distinct()
    categoryOpen3 = list(categoryOpen3_query)
    cobj3 = {}
    for x in categoryOpen3:
        cat_count = InAppAds.objects.filter(ad_id3=0,category=x).count()
        cobj3[x] = cat_count

    
    ads = Advertisement.objects.filter(user_id=user_id,ad_type='inapp')

    return render(request,'iCategoryslots.html',{'cobj3' : cobj3,'ads' : ads})

@login_required
def purchaseICslots(request):
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
        print("slots purchased")
        return redirect('iCategoryslots')