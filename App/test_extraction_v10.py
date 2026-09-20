import unittest
from unittest.mock import patch
from services.document_answers import consensus,read_key
class ExtractionTests(unittest.TestCase):
 def test_conflicting_reads(self):
  self.assertEqual(consensus(['A','A','']),'A')
  for reads in (['A','B','A'],['A','',''],['','','']): self.assertEqual(consensus(reads),'REVIEW')
 def test_scanned_key_disagreement(self):
  with patch('services.document_answers._read_key',side_effect=[({1:'A',2:'B'},True),({1:'A',2:'C'},True)]):
   self.assertEqual(read_key(b'','a.pdf','A'),{1:'A',2:'REVIEW'})
 def test_text_key_no_ocr_retry(self):
  with patch('services.document_answers._read_key',return_value=({1:'D'},False)) as reader:
   self.assertEqual(read_key(b'','a.pdf','A'),{1:'D'})
   self.assertEqual(reader.call_count,1)
