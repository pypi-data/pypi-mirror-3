from django.test import TestCase
from django.db.models import Model
from django.db import IntegrityError
from ipyfield.models import IPyField
import IPy
from IPy import IP


class DummyModel(Model):
    field = IPyField()
    null_field = IPyField(null=True)

    def __str__(self):
        return '<DummyModel %s>' % self.pk

    __repr__ = __str__


class IPySubclassTests(TestCase):
    def test_ipyfield_can_compare_to_non_IP(self):
        self.assertNotEqual(IP('::1').strNormal(), 'foo')
        self.assertNotEqual(IP('::1').int(), 22)

    def test_IPy_cant_compare_to_non_IP(self):
        with self.assertRaises(AttributeError):
            self.assertNotEqual(IPy.IP('::1'), 'foo')
        with self.assertRaises(AttributeError):
            self.assertNotEqual(IPy.IP('::1'), 22)

class IPyFieldTests(TestCase):

    def setUp(self):
        self.obj = DummyModel()

    def test_empty(self):
        self.assertEqual(None, self.obj.field)

    def test_iptype(self):
        self.obj.field = '127.0.0.1'
        self.assertEqual(self.obj.field.iptype(),'PRIVATE')
        self.obj.field = '100.80.90.100'
        self.assertEqual(self.obj.field.iptype(), 'PUBLIC')


    def test_range_lookups(self):
        ip_block = IP('127.0.0.0/28')
        [DummyModel.objects.create(field=ip) for ip in ip_block]
        self.assertEqual(16, len(ip_block), DummyModel.objects.count())
        self.assertTrue(DummyModel.objects.count() >
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30'))\
               .count())
        self.assertEqual(4, DummyModel.objects.filter(
               field__in=IP('127.0.0.0/30')).count())
        # testing lookups work with str as __in param rather than
        # requiring an IP instance
        self.assertQuerysetEqual(
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30')),
               [repr(o) for o in DummyModel.objects.filter(
                                            field__in='127.0.0.0/30')])

        self.assertQuerysetEqual(
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30')),
               [repr(o) for o in DummyModel.objects.filter(
                               field__in='127.0.0.0/255.255.255.252')])

        self.assertQuerysetEqual(
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30')),
               [repr(o) for o in DummyModel.objects.filter(
                                     field__in='127.0.0.0-127.0.0.3')])
        # flat list of string addresses should also work the same
        self.assertQuerysetEqual(
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30')),
               [repr(o) for o in DummyModel.objects.filter(
                                   field__in=['127.0.0.0', '127.0.0.1',
                                              '127.0.0.2', '127.0.0.3'])])


    def test_required_values(self):
        with self.assertRaises(IntegrityError):
            # non-null field should require value
            DummyModel.objects.create()

    def test_null_values(self):
        # null field can be left empty
        DummyModel.objects.create(field='::1')

    def test_ipv6_support(self):
        obj = DummyModel.objects.create(field='2001:dead:beef::1')
        self.assertEqual(obj.field.version(), 6)

    def test_valid_lookups(self):
        with self.assertRaises(TypeError):
            # it's possible people will forget this is not a char/text field.
            DummyModel.objects.filter(field__startswith='127.0.0')

        
        DummyModel.objects.filter(field__gt=1000)
        DummyModel.objects.filter(field__gte=1000)
        DummyModel.objects.filter(field__lt=1000)
        DummyModel.objects.filter(field__lte=1000)

        # all valid, but won't return anything....
        DummyModel.objects.filter(field=1000)
        DummyModel.objects.filter(field__exact='127.0.0')
        DummyModel.objects.filter(field__in=[1,2,3])

    def test_max_values(self):
        DummyModel.objects.create(field='ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')
        DummyModel.objects.create(field='255.255.255.255')



