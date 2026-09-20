"""Shared marksheet totals and printable certificate."""
from html import escape
from config import PAPERS, QUALIFYING_PERCENT


def overall_status(results):
    if any(p not in results for p in PAPERS):
        return 'PENDING — incomplete result'
    if all(results[p]['percentage'] >= QUALIFYING_PERCENT for p in ('p1','p2')):
        return 'PASS — eligible for merit ranking'
    return 'FAIL — qualifying requirement not met'


def total_rows(results):
    rows=[]
    for label, papers, category in [('QUALIFYING TOTAL',('p1','p2'),'Qualifying only'),
                                    ('MERIT TOTAL',('p3','p4','p5','p6'),'Ranking marks'),
                                    ('GRAND TOTAL',tuple(PAPERS),'All papers; not ranking marks')]:
        complete=all(p in results for p in papers)
        row=dict(Paper=label,Subject='',Category=category)
        if complete:
            score=sum(results[p]['score'] for p in papers)
            maximum=sum(results[p]['max_score'] for p in papers)
            row.update(Score=round(score,2),Maximum=round(maximum,2),Percentage=round(score/maximum*100,2) if maximum else 0)
            for column,field in [('Correct','correct'),('Wrong','wrong'),('Unanswered','unanswered'),('Deleted','bonus')]:
                row[column]=sum(results[p][field] for p in papers)
            row['Status']=('PASS' if all(results[p]['percentage']>=QUALIFYING_PERCENT for p in papers) else 'FAIL') if label=='QUALIFYING TOTAL' else ('Merit only' if label=='MERIT TOTAL' else overall_status(results))
        else:
            row.update(Score=None,Maximum=None,Percentage=None,Status='PENDING')
        rows.append(row)
    return rows


def certificate_html(frame,results,name,roll,exam):
    status=overall_status(results)
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Result certificate</title>
<style>body{{font:16px Arial;margin:40px;color:#172b4d}}h1{{text-align:center}}table{{border-collapse:collapse;width:100%;font-size:12px}}td,th{{border:1px solid #bbc;padding:7px;text-align:left}}th{{background:#eef3f8}}.status{{padding:15px;border:2px solid #345;font-weight:bold}}@media print{{button{{display:none}}body{{margin:12mm}}}}</style></head><body>
<h1>Examination Result Certificate</h1><p>Candidate: {escape(name)}<br>Roll number: {escape(roll)}<br>Exam: {escape(exam)}</p>
<p class="status">{escape(status)}</p>
{frame.fillna('—').to_html(index=False,escape=True,border=0)}
<p>English and Hindi must each reach {QUALIFYING_PERCENT:g}%. Their marks do not count towards merit. Merit uses P3–P6 only. PASS indicates qualifying eligibility, not selection or appointment.</p>
<p>App-generated statement based on reviewed entries and the configured marking scheme; not an official examination authority certificate.</p>
<button onclick="window.print()">Print / Save as PDF</button></body></html>'''
