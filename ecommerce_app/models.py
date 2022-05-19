from django.db import models
from django.urls import reverse
from accounts.models import Account

# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=250, unique=True)
    slug=models.SlugField(max_length=250, unique= True)
    desc=models.TextField(blank=True)
    cat_offer = models.IntegerField(null=True)
    image1=models.ImageField(upload_to='category',blank=True)
    created=models.DateField(auto_now=True)
    updated=models.DateField(auto_now=True)
    class Meta:
        ordering=('name',)
        verbose_name='Category'
        verbose_name_plural='categories'

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=250, unique= True)
    slug = models.SlugField(max_length=250, unique= True)
    desc = models.TextField(blank=True)
    image1 = models.ImageField(upload_to='product', blank=True)
    image2 = models.ImageField(upload_to='product', blank=True)
    image3 = models.ImageField(upload_to='product', blank=True)
    image4 = models.ImageField(upload_to='product', blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    actual_price = models.IntegerField(null=True)
    offer = models.IntegerField(null=True)
    stock=models.IntegerField()
    available=models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now_add=True)

    def get_url(self):
        return reverse('single_view', args=[self.category.slug,self.slug])


    def __str__(self):
        return self.name


@property
def image_url(self):
    if self.image and hasattr(self.image, 'url'):
        return self.image1.url


# class Order(models.Model):
#     user = models.ForeignKey(Account, on_delete=models.CASCADE)
#     item = models.ForeignKey(Product, on_delete=models.CASCADE)
#     total = models.FloatField()
#     pay_method = models.CharField(max_length=10)
#     order_status = models.CharField(max_length=20, default="Placed")
#     quantity = models.IntegerField()
#     start_date = models.DateField(auto_now_add=True)
#     start_time = models.TimeField(auto_now_add=True)


