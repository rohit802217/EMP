"""Six-paper extraction with mandatory review before publishing."""
import hashlib
import json
import pandas as pd
import streamlit as st
from config import PAPERS, QUALIFYING_PERCENT
from services.result_certificate import total_rows, overall_status, certificate_html
from services.document_answers import read_key, read_bpsc_summary
from services.six_paper_service import parse_uploaded_answers, parse_deleted_questions, evaluate_paper, build_candidate, save_candidate

@st.cache_data(show_spinner=False)
def extract(data,filename,series,role):
    return read_key(data,filename,series) if role=='key' else read_bpsc_summary(data,filename,series)

def result_frame(results):
    rows=[]
    for p,meta in PAPERS.items():
        r=results.get(p)
        row=dict(Paper=p.upper(),Subject=meta['subject'],Category=meta['category'])
        if r is None:
            row.update(Score=None,Maximum=None,Percentage=None,Status='Missing / review required')
        else:
            row.update(Correct=r['correct'],Wrong=r['wrong'],Unanswered=r['unanswered'],Deleted=r['bonus'],
                       Score=r['score'],Maximum=r['max_score'],Percentage=r['percentage'],
                       Status=('PASS' if r['percentage']>=QUALIFYING_PERCENT else 'FAIL') if p in ('p1','p2') else 'Merit paper')
        rows.append(row)
    return pd.DataFrame(rows+total_rows(results))

def present_results(results):
    st.subheader('Six-paper marksheet')
    frame=result_frame(results)
    st.dataframe(frame,hide_index=True,width='stretch')
    status=overall_status(results)
    (st.success if status.startswith('PASS') else st.error if status.startswith('FAIL') else st.warning)(status)
    st.caption(f'English and Hindi must each reach {QUALIFYING_PERCENT:g}%. Only P3–P6 count towards merit. Grand total is informational.')
    st.download_button('Download marksheet CSV',frame.to_csv(index=False),'six_paper_marksheet.csv','text/csv')
    if len(results)==6:
        html=certificate_html(frame,results,st.session_state.get('six_name',''),st.session_state.get('six_roll',''),st.session_state.get('six_exam',''))
        st.download_button('Download printable result certificate',html,'result_certificate.html','text/html')
        st.caption('Open the downloaded certificate and choose Print / Save as PDF.')

def render_six_paper_page():
    st.subheader('Six-paper upload, review and evaluation')
    st.caption('Version 10 — three-pass response OCR and focused correction of uncertain answers.')
    notice=st.session_state.pop('six_save_notice',None)
    if notice:
        st.success(notice)
    name=st.text_input('Student Name',key='six_name')
    roll=st.text_input('Roll Number',key='six_roll')
    exam=st.text_input('Exam / recruitment ID (use the same ID for candidates in one leaderboard)',key='six_exam')
    a,b,c=st.columns(3)
    correct=a.number_input('Marks per correct answer',min_value=0.01,value=1.0)
    penalty=b.number_input('Penalty per wrong/multiple answer',min_value=0.0,value=1.0)
    bonus=c.number_input('Marks per deleted question',min_value=0.0,value=2.0)
    st.caption('Confirm the official marking scheme. Defaults are unverified. Unanswered = 0; negative totals are floored at 0. Deleted marks replace normal marks in the maximum.')
    inputs={}
    for p,meta in PAPERS.items():
        with st.expander(f"{meta['code']} — {meta['subject']} ({meta['category']})"):
            series=st.selectbox('Booklet series',list('ABCDEFGHIJKL'),key=p+'_series')
            count=int(st.number_input('Expected questions',min_value=1,max_value=500,value=50,key=p+'_count'))
            mode=st.selectbox('Response layout',['BPSC 50-question summary (supplied layout)','Manual review / CSV / JSON'],key=p+'_mode')
            response=st.file_uploader('Response sheet',type=['pdf','png','jpg','jpeg','csv','json'],key=p+'_response')
            key=st.file_uploader('Official key',type=['pdf','png','jpg','jpeg','csv','json'],key=p+'_key')
            deleted=st.text_input('Additional deleted questions',key=p+'_deleted')
            st.caption('Verify subject and examination match. This template reads the printed summary, not arbitrary bubbles or cropped scans.')
            inputs[p]=(series,count,mode,response,key,deleted)
    identity=[(p,s,n,m,hashlib.sha256(r.getvalue()).hexdigest() if r else '',hashlib.sha256(k.getvalue()).hexdigest() if k else '',d) for p,(s,n,m,r,k,d) in inputs.items()]
    signature=hashlib.sha256(json.dumps([identity,name,roll,exam,correct,penalty,bonus]).encode()).hexdigest()
    if st.session_state.get('six_result_signature')!=signature:
        st.session_state.pop('six_final',None)
        st.session_state.pop('six_preview',None)
        st.session_state['six_result_signature']=signature
    hashes={}
    for p,s,n,m,r,k,d in identity:
        if r:
            hashes.setdefault(r,[]).append(p.upper())
    duplicates=[papers for papers in hashes.values() if len(papers)>1]
    for papers in duplicates:
        st.error('Identical response file uploaded for '+', '.join(papers)+'. Replace the incorrect upload. Overall saving is blocked.')
    if st.button('1. Extract uploaded papers',type='primary'):
        st.session_state.pop('six_review',None)
        st.session_state.pop('six_final',None)
        if not any(r and k for s,n,m,r,k,d in inputs.values()):
            st.error('Upload at least one response sheet and its matching key.')
        else:
            tables={}
            for p,(series,count,mode,response,key,deleted) in inputs.items():
                if not response or not key:
                    st.warning(p.upper()+': upload both files to include this paper.')
                    continue
                keys={};answers={}
                try:
                    with st.spinner(f'Reading {p.upper()} — OCR may take a minute...'):
                        keys=parse_uploaded_answers(key) if key.name.lower().endswith(('.csv','.json')) else extract(key.getvalue(),key.name,series,'key')
                        if response.name.lower().endswith(('.csv','.json')):
                            answers=parse_uploaded_answers(response)
                        elif mode.startswith('BPSC'):
                            if count!=50:
                                raise ValueError('BPSC template requires 50 questions.')
                            answers=extract(response.getvalue(),response.name,series,'response')
                except Exception as exc:
                    st.error(f'{p.upper()}: {exc}. Review manually; no result saved.')
                if set(keys)!=set(range(1,count+1)):
                    st.warning(p.upper()+': key count differs from expected; verify all key cells.')
                tables[p]=pd.DataFrame([{'Question':q,'Response':answers.get(q,'REVIEW'),'Key':keys.get(q,'REVIEW')} for q in range(1,count+1)])
            st.session_state['six_review']=(signature,tables)
    stored=st.session_state.get('six_review')
    if not stored:
        return
    if stored[0]!=signature:
        st.warning('Uploads/settings changed. Extract again.')
        return
    st.subheader('Extraction results')
    st.caption('Only uncertain answers need correction. Accepted OCR can still contain errors; you can inspect or correct all answers. BLANK means genuinely unanswered; * means multiple marks.')
    reviewed={}
    for p,table in stored[1].items():
        uncertain=(table.Response=='REVIEW') | (table.Key=='REVIEW')
        with st.expander(f'{p.upper()} — {int(uncertain.sum())} uncertain questions',expanded=bool(uncertain.any())):
            show_all=st.checkbox('Show all questions',key='all_'+p+'_'+signature)
            subset=table if show_all else table.loc[uncertain]
            updated=table.copy()
            if not subset.empty:
                edits=st.data_editor(subset,hide_index=True,disabled=['Question'],width='stretch',column_config={'Response':st.column_config.SelectboxColumn(options=['A','B','C','D','BLANK','*','REVIEW']),'Key':st.column_config.SelectboxColumn(options=['A','B','C','D','DELETED','REVIEW'])},key='review_'+p+'_'+signature+'_'+str(show_all))
                updated.loc[edits.index,['Response','Key']]=edits[['Response','Key']]
            else:
                st.success('No unresolved cells. Ready to calculate.')
            reviewed[p]=updated
    confirmed=st.checkbox('The subjects, booklet sets and marking rules match this examination.',key='confirm_'+signature)
    if st.button('2. Calculate reviewed papers / save complete result'):
        if not name.strip() or not roll.strip() or not confirmed:
            st.error('Enter name/roll and confirm the review.')
            return
        try:
            results={}
            for p,df in reviewed.items():
                if any(p.upper() in group for group in duplicates):
                    st.warning(p.upper()+': duplicate upload; excluded until corrected.')
                    continue
                answers=dict(zip(df.Question.astype(int),df.Response))
                keys=dict(zip(df.Question.astype(int),df.Key))
                try:
                    if any(v not in ('A','B','C','D','DELETED') for v in keys.values()):
                        raise ValueError('Unresolved key cells.')
                    results[p]=evaluate_paper(answers,keys,parse_deleted_questions(inputs[p][5]),correct,penalty,bonus)
                except ValueError as exc:
                    st.warning(p.upper()+': '+str(exc))
                    continue
                results[p]['series']=inputs[p][0]
            if results:
                st.session_state['six_preview']=(signature,results)
            if len(results)!=6 or duplicates:
                st.warning('Partial preview only. Qualification and overall rank are unavailable until all six valid, distinct sheets are reviewed. Nothing saved.')
                present_results(results)
                return
            candidate=build_candidate(name,roll,results)
            if not exam.strip():
                st.error('Enter the exam / recruitment ID before saving and ranking.')
                present_results(results)
                return
            candidate['exam_id']=exam.strip()
            candidate['reviewed_complete']=True
            candidate['marking_scheme']=dict(correct=correct,wrong_penalty=penalty,deleted=bonus)
            candidate,_=save_candidate(candidate)
            st.session_state['six_final']=candidate
            st.session_state['six_save_notice']=f"Result saved and leaderboard updated for {candidate['name']} (roll {candidate['roll_no']}). Open Live Leaderboard to view it."
            st.session_state['leaderboard_search']=''
            st.session_state['leaderboard_exam']='All exams'
            st.rerun()
        except Exception as exc:
            st.error(f'Review required: {exc} No result saved.')
    candidate=st.session_state.get('six_final')
    if candidate:
        st.subheader(f"Saved: {candidate['name']} ({candidate['roll_no']})")
        st.write(f"{candidate['status']} · Merit {candidate['raw_merit_total']} / {candidate['merit_max']} · App rank {candidate.get('rank') or 'Not eligible'} · {candidate.get('ranked_candidates',0)} comparable qualified candidates")
        st.caption('App rank uses reviewed candidates saved here for the same exam and marking scheme. It is not an official examination rank. Equal scores share rank.')
        present_results(candidate['papers'])
    elif st.session_state.get('six_preview',('',))[0]==signature:
        st.info('Calculated preview — not saved to the leaderboard.')
        present_results(st.session_state['six_preview'][1])
