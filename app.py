from flask import Flask, request, render_template, url_for, redirect
import os
import pandas as pd

app = Flask(__name__)

@app.route('/create', methods=['POST'])
def create_certificate():

    data = request.form
    
    result = {}
    experiences = {}

    for key, value in data.items():
        if '[' in key and ']' in key:
            main_key, rest = key.split("[", 1)
            idx, rest = rest.split("][", 1)
            sub_key = rest.rstrip(']')
            
            if main_key not in experiences:
                experiences[main_key] = {}
            
            if idx not in experiences[main_key]:
                experiences[main_key][idx] = {}
            
            experiences[main_key][idx][sub_key] = value
        else:
            result[key] = value

    for key, file in request.files.items():
        main_key, rest = key.split("[", 1)
        idx, rest = rest.split("][", 1)
        sub_key = rest.rstrip(']')
        
        if main_key not in experiences:
            experiences[main_key] = {}
        
        if idx not in experiences[main_key]:
            experiences[main_key][idx] = {}
        
        filename = file.filename
        if filename != '':
            experiences[main_key][idx][sub_key] = filename

            cert_name = data["certificate-name"]
            save_path = os.path.join("uploads", cert_name)
            os.makedirs(save_path, exist_ok=True)
            print(filename)
            file.save(os.path.join(save_path, filename))

    result['experiences'] = [experiences['experiences'][k] for k in sorted(experiences['experiences'].keys())]

    cert_name = result["certificate-name"]
    rows = []
    for exp in result['experiences']:
        row = {}
        row["certificate-name"] = cert_name
        row["experience-name"] = exp["name"]
        row["experience-text"] = exp.get("text", "")
        row["experience-data"] = exp.get("data", "")
        rows.append(row)

    # Converting the flattened data to a DataFrame
    df = pd.DataFrame(rows)
    df.to_csv('output.csv',mode='a',header=False, index=False)

    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)