import unittest
from copy import deepcopy
from services.six_paper_service import evaluate_paper
from services.leaderboard_service import recalculate_ranks
class V6Tests(unittest.TestCase):
 def test_unresolved_key(self):
  with self.assertRaises(ValueError): evaluate_paper({1:'A'},{1:'REVIEW'},set())
 def test_ranking(self):
  base=dict(reviewed_complete=True,qualifying_pass=True,exam_id='Exam',marking_scheme={'correct':1},papers={f'p{i}':{'max_score':50} for i in range(1,7)})
  rows=[]
  for i,score in enumerate([100,100,90,120,130,140]):
   row=deepcopy(base);row.update(roll_no=str(i),merit_total=score);rows.append(row)
  rows[3]['qualifying_pass']=False
  rows[4]['reviewed_complete']=False
  rows[5]['exam_id']='Other'
  ranked={r['roll_no']:r for r in recalculate_ranks(rows)}
  self.assertEqual([ranked[str(i)]['rank'] for i in range(6)],[1,1,3,None,None,1])
  self.assertEqual(ranked['0']['ranked_candidates'],3)

class SaveTests(unittest.TestCase):
 def test_save_update_and_render(self):
  import tempfile
  from pathlib import Path
  from unittest.mock import patch
  from services.six_paper_service import build_candidate,save_candidate
  from services.leaderboard_service import load_data
  from streamlit.testing.v1 import AppTest
  paper=evaluate_paper({1:'A'},{1:'A'},set())
  candidate=build_candidate('Saved candidate','001',{f'p{i}':dict(paper) for i in range(1,7)})
  candidate.update(exam_id='Test',reviewed_complete=True,marking_scheme={'correct':1})
  with tempfile.TemporaryDirectory() as d, patch('services.leaderboard_service.DATA_FILE',str(Path(d)/'leaderboard.json')):
   save_candidate(candidate)
   candidate.update(name='Updated candidate',qualifying_pass=False,status='Disqualified',merit_total=0)
   save_candidate(candidate)
   self.assertEqual(len(load_data()),1)
   app=AppTest.from_string('from ui.leaderboard_page import render_leaderboard_page\nrender_leaderboard_page()').run()
   self.assertFalse(app.exception)
   frame=app.dataframe[0].value
   self.assertEqual(frame.iloc[0]['Candidate Name'],'Updated candidate')
   self.assertEqual(frame.iloc[0]['Merit Score'],4)
