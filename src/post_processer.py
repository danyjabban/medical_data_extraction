from docx import Document

def post_processor(answers):
    processed_answers = process_answers(answers)
    create_doc(processed_answers)

def process_answers(answers):
    processed_answers = {}
    for query in answers.keys():
        processed_answers[query] = {}
        for page_ans in answers[query]:
            print(page_ans)
            page_idx = page_ans[0]
            print(page_idx)
            for k, v in page_ans[1].items():
                k_standard = convert_str_standard(k)
                if k_standard in processed_answers[query]:
                    cur = v
                    prev = processed_answers[query][k_standard]
                    # if replace:

                else:
                    processed_answers[query][k_standard] = [v, page_idx]

    return processed_answers


# def compare_cur_prev_answers(cur, prev):
#     if None in cur:


def convert_str_standard(string):
    string = string.lower()
    string = string.replace('\n',' ') 
    string = string.strip()
    return string


def create_doc(answers):
    print(answers)
    document = Document()
    for k, v in answers.items():
        document.add_heading(f'{k}', level=1)
        for ans_k, ans_v in answers[k].items():
            document.add_paragraph(f'medication: {ans_k}\n start and stop dates: {ans_v[0]}\n page(s) found: {ans_v[1]}')
    document.save('docx_file.docx')
    

# docx_test()

if __name__ == "__main__":
    # d = {'medication': [{51: {'Cymbalta': (None, None), 'temazepam': (None, None), 'trazodone': (None, None)}}, {111: {'Citalopram (Celexa) 20 MG Tab': ('04/10/2018', '10/20/2018'), 'Norethindrone Ac-Eth Estradiol ( Norethind-Eth Estrad 1-0.02 Mg) 1 Each Tablet': ('04/04/2018', '04/10/2018'), 'Trazodone (Desyrel) 50 MG Tab': ('12/28/2017', '07/16/2018'), 'Citalopram (Celexa) 10 MG Tab': ('12/28/2017', '04/10/2018'), 'Trazodone': ('12/28/2017', '07/16/2018'), 'Citalopram': ('10/19/2017', '12/28/2017'), 'Hydroxyzine Hcl': ('12/06/2017', '12/28/2017'), 'Trazodone Hcl': ('12/06/2017', '12/28/2017')}}]}
    d = {'medication': [[51, {'Cymbalta': (None, None), 'temazepam': (None, None), 'trazodone': (None, None)}], [111, {'Citalopram (Celexa) 20 MG Tab': [('07/16/2018', '09/18/2018'), ('04/20/2018', '07/16/2018'), ('04/20/2018', '04/20/2018'), ('04/10/2018', '10/4/20/2018')], 'Citalopram (Celexa) 20 MG Tab\nNorethindrone Ac-Eth Estradiol\n(Norethind-Eth Estrad 1-0.02 Mg) 1 EA\nTablet': [('04/04/2018', '04/10/2018')], 'Norethindrone Ac-Eth Estradiol\n(Norethind-Eth Estrad 1-0.02 Mg) 1 EA\nTablet': [('04/04/2018', '04/10/2018')], 'Trazodone (Desyrel) 50 MG Tab': [('12/28/2017', '07/16/2018')], 'Citalopram (Celexa) 10 MG Tab': [('12/28/2017', '07/16/2018'), ('12/28/2017', '04/10/2018')], 'Trazodone': [('12/28/2017', '07/16/2018')], 'Citalopram': [('12/28/2017', '04/10/2018'), ('10/19/2017', '12/28/2017')], 'Hydroxyzine Hcl': [('12/06/2017', '12/28/2017'), ('12/06/2017', '12/28/2017'), ('12/06/2017', '12/28/2017'), ('12/06/2017', '12/28/2017'), ('12/06/2017', '12/28/2017')], 'Trazodone Hcl': [('12/06/2017', '12/28/2017'), ('12/06/2017', '12/28/2017'), ('12/06/2017', '12/28/2017')]}]]}
    # process_answers(d)
    post_processor(d)