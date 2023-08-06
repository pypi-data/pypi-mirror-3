import os
from unittest import skipUnless
from decimal import Decimal
from django.conf import settings
from django.test import TestCase
from django.core.files import File
from ccstraps.models import Strap, StrapImage



red = os.path.exists('%s/ccstraps/red.png' % settings.STATIC_ROOT)
purple = os.path.exists('%s/ccstraps/purple.png' % settings.STATIC_ROOT)
class ModelTestCases(TestCase):



    def test_created_added_to_strap_when_save(self):
        """When a strap is saved the created date is saved"""
        s = Strap()
        s.name = 'test'
        s.save()
        self.assertTrue(s.created)


    def test_name_contains_only_alpha_numberics(self):
        """ When a model is saved the name is lowercased and slugified"""
        s = Strap()
        s.name = 'Test Slug!'
        s.save()
        self.assertEqual(s.name, 'test-slug')

    @skipUnless(red, 'red.png file does not exist')
    @skipUnless(purple, 'purple.png file does not exist')
    def test_strap_image_ordering(self):
        """Strap imags should be ordered by their order attribute"""
        s = Strap()
        s.name = 'test'
        s.save()
        # now create the strap image
        r = open('%s/ccstraps/red.png' % settings.STATIC_ROOT)
        s1  = StrapImage()
        s1.src = File(r, 'ccstraps/red.png')
        s1.order = Decimal('10.00')
        s1.strap = s
        s1.save()
        # Another
        p = open('%s/ccstraps/purple.png' % settings.STATIC_ROOT)
        s2  = StrapImage()
        s2.src = File(r, 'ccstraps/purple.png')
        s2.order = Decimal('1.00')
        s2.strap = s
        s2.save()
        # close the images
        r.close()
        p.close()
        # now the order of the straps is s2, s1
        self.assertEqual(s.strapimage_set.all()[0].pk, s2.pk)
        self.assertEqual(s.strapimage_set.all()[1].pk, s1.pk)
        # change the order around
        s1.order = Decimal('2')
        s1.save()
        s2.order = Decimal('3')
        s2.save()
        # now the order has change
        self.assertEqual(s.strapimage_set.all()[0].pk, s1.pk)
        self.assertEqual(s.strapimage_set.all()[1].pk, s2.pk)
