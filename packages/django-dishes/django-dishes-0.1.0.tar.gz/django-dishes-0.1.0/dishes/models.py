from datetime import datetime, date, timedelta
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel, TitleSlugDescriptionModel
from django_extensions.db.fields import AutoSlugField

from shop.models import Product
from dishes.managers import ActiveManager
from dishes.utils import units
from dishes.templatetags.dishes_filters import text_fraction
#from markup_mixin.models import MarkupMixin

class Category(TitleSlugDescriptionModel):

    class Meta:
        verbose_name=_('Category')
        verbose_name_plural=_('Categories')

    def __unicode__(self):
        return self.title

class Ingredient(TimeStampedModel):
    '''
    A generic ingredient model, for all your summer squash, haddock filets, flank steaks, etc... needs.
    '''
    name=models.CharField(_('Name'), max_length=100)
    description=models.TextField(_('Description'), blank=True, null=True)
    category=models.ForeignKey(Category)

    class Meta:
        verbose_name=_('Ingredient')
        verbose_name_plural=_('Ingredients')

    def __unicode__(self):
        return u'%s' % self.name

class IngredientAmount(TimeStampedModel):
    ingredient=models.ForeignKey(Ingredient)
    quantity=models.DecimalField(_('Quantity'), max_digits=5, decimal_places=2)
    unit=models.CharField(_('Unit'), choices=units.UNIT_CHOICES, max_length=3, blank=True, null=True)
    note=models.CharField(_('Note'), blank=True, null=True, max_length=255)
    source=models.CharField(_('Source'), blank=True, null=True, max_length=255, help_text='Local farm, maybe?')

    class Meta:
        verbose_name=_('Recipe ingredient')
        verbose_name_plural=_('Recipe ingredients')

    def __unicode__(self):
        if self.unit:
            return ' '.join([self.ingredient.name, text_fraction(self.quantity), self.unit])
        else:
            return ' '.join([str(self.quantity), self.ingredient.name])

#class Recipe(MarkupMixin, TitleSlugDescriptionModel, TimeStampedModel):
class Recipe(TitleSlugDescriptionModel, TimeStampedModel):
    TYPE_CHOICES=(('main', 'Main course'), ('side','Side dish'), ('starch', 'Starch'))

    ingredient_amounts=models.ManyToManyField(IngredientAmount, blank=True, null=True)
    rendered_description=models.TextField(_('Rendered description'), blank=True, null=True)
    note=models.TextField(_('Note'), blank=True, null=True, help_text='Notes for the chef, not shown to the public.')
    type=models.CharField(_('Type'), choices=TYPE_CHOICES, default='main', max_length=100)

    @property
    def build_shopping_list(self):
        pass

    @property
    def menu_frequency(self):
        pass

    class Meta:
        verbose_name=_('Recipe')
        verbose_name_plural=_('Recipes')

    class MarkupOptions:
        source_field = 'description'
        rendered_field = 'rendered_description'

    def __unicode__(self):
        return u'%s' % self.title

class Dish(Product):
    """
    Dish model class.

    A simple model to represent a dish.
    """
    start=models.DateField(_('Start date'), default=datetime.now())
    end=models.DateField(_('End date'), blank=True, null=True)
    content=models.TextField(_('Content'))
    author=models.ForeignKey(User, blank=True, null=True)
    main_course=models.ForeignKey(Recipe, related_name='main_course_recipe')
    side_courses=models.ManyToManyField(Recipe, related_name='side_course_recipes')
    rendered_content=models.TextField(_('Rendered description'), blank=True, null=True)
    photo=models.ImageField(_('Photo'), blank=True, null=True, upload_to='dishes/')
  
    #active_objects = ActiveManager()
    #objects = models.Manager()

    @property
    def on_active_menu(self): 
        pass
        #(Is the dish currently being offered, used as a check before filling orders)

    class Meta:
        verbose_name=_('Dish')
        verbose_name_plural=_('Dishes')

    class MarkupOptions:
        source_field = 'content'
        rendered_field = 'rendered_content'

    def __unicode__(self):
        return u'%s' % (self.name)

    @models.permalink
    def get_absolute_url(self):
        return ('dh-dish-detail', None, {'slug': self.slug })


class Delivery(TimeStampedModel):
    date=models.DateField(_('Date'))
    order_deadline=models.DateField(_('Order deadline'), blank=True, null=True)

    class Meta:
        verbose_name=_('Delivery')
        verbose_name_plural=_('Deliveries')

    def past_deadline(self):
        if self.order_deadline <= date.today():
            return True
        else:
            return False

    def __unicode__(self):
        return u'%s' % (self.date.strftime("%a, %b %e"))

class Menu(TimeStampedModel):
    slug=models.SlugField(_('Slug'), blank=True, null=True)
    dishes=models.ManyToManyField(Dish)
    publish_date=models.DateField(_('Publish date'), blank=True, null=True, default=datetime.now())
    expire_date=models.DateField(_('Expiration date'), blank=True, null=True, default=datetime.now()+timedelta(days=7))
    deliveries=models.ManyToManyField(Delivery, blank=True, null=True)
    created_by=models.ForeignKey(User)

    objects = models.Manager()
    active_objects = ActiveManager()
    class Meta:
        verbose_name=_('Menu')
        verbose_name_plural=_('Menus')

    @property
    def live(self):
        # A menu is live if a) it has been published and b) there are still active delivery dates
        live=False
        if self.publish_date >= date.today():
            for delivery in self.deliveries.all():
                if not delivery.past_deadline():
                    live= True
        return live 

    def save(self, *args, **kwargs):
        super(Menu, self).save(*args, **kwargs)
        self.slug = self.publish_date.strftime("%b-%e").lower().replace(' ','')
        super(Menu, self).save()

    def __unicode__(self):
        return u' '.join(['Menu for', self.publish_date.strftime("%a, %b %e")])

    @models.permalink
    def get_absolute_url(self):
        return ('ds-menu-detail', None, {'slug': self.slug})

    
