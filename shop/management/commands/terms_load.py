from django.core.management import BaseCommand
import csv
from shop.models import Category


class Command(BaseCommand):
    help = 'Parse terms.csv and load it into the database'
    terms = []
    csvfile = 'terms.csv'

    def handle(self, *args, **options):
        self.parse_csv_file()
        self.load_terms()
        self.set_relationships()

    def parse_csv_file(self):
        """
        Uses self.csvfile and save data to self.terms attribute
        :return: None
        """
        with open(self.csvfile, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                self.terms.append(row)

    def load_terms(self):
        """
        Uses self.terms and load terms into database
        :return: count of loaded terms
        """
        counter = 0
        for term in self.terms:
            source_id = term.get('group_id')
            if source_id is None:
                continue

            term_name_ru = term.get('group_name')
            term_name_ua = term.get('group_name_ua')
            parent_id = term.get('parent_group_id')
            if term_name_ru is None and term_name_ua is None:
                continue

            try:
                Category.objects.get(source_id=source_id)
            except Category.DoesNotExist:
                name_ua = term_name_ua or term_name_ru
                name_ru = term_name_ru or term_name_ua
                Category.add_root(name_ua=name_ua, name_ru=name_ru,
                                      source_id=source_id)
            counter += 1

        return counter

    def set_relationships(self):
        """
        Loop self.terms and set parent term
        :return: None
        """
        for term in self.terms:
            parent_id = term.get('parent_group_id')
            if parent_id is None or parent_id == '':
                continue
            parent_term = Category.objects.get(source_id=parent_id)

            source_id = term.get('group_id')
            if source_id is None:
                continue
            current_term = Category.objects.get(source_id=source_id)
            current_term.move(parent_term, 'sorted-child')

