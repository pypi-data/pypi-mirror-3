#!/usr/bin/env python
# coding: utf-8

import os
os.environ['DJANGO_SETTINGS_MODULE'] = "reversion_compare_test_project.settings"

import reversion
from reversion_compare_test_project.reversion_compare_test_app.models import Pet, \
    Person


if __name__ == "__main__":
    with reversion.create_revision():
        pet1 = Pet.objects.create(name="Catworth")
        pet2 = Pet.objects.create(name="Dogwoth")
        person = Person.objects.create(name="Dave")
        person.pets.add(pet1, pet2)

    print "version 1:", person, person.pets.all()
    # Dave [<Pet: Catworth>, <Pet: Dogwoth>]

    with reversion.create_revision():
        pet1.name = "Catworth the second"
        pet1.save()
#        person.pets.remove(pet2)
#        person.save()
        pet2.save()
        pet2.delete()
        person.save()

    print "version 2:", person, person.pets.all()
    # Dave [<Pet: Catworth the second>]
