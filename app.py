from flask import Flask, jsonify, Response
import requests, csv, io

app = Flask(__name__)

# Settings
API_URL = "https://sidebar.stract.to/api"
AUTH_TOKEN = "ProcessoSeletivoStract2025"

# Function to get the data from the API
def get_data():
    url = f"{API_URL}/platforms"
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Falha ao buscar dados"}
    
@app.route('/')
def home():
    return jsonify({
        "name": "Jefferson Silemen Vasconcelos Vieira de Paula",
        "email": "jeffersonvieiratec@gmail.com",
        "linkedin": "https://www.linkedin.com/in/jeffersonsilemen/"
    })

@app.route('/platforms')
def platforms():
    data = get_data()
    return jsonify(data)

# Getting accounts on a especific platform
def get_accounts(platform):
    all_accounts = []
    page = 1

    while True:
        url = f"{API_URL}/accounts?platform={platform}&page={page}"
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Check if there are accounts on actual page
            if "accounts" in data and data["accounts"]:
                all_accounts.extend(data["accounts"])
                page += 1
            else:
                break
        else:
            break
    return all_accounts
    
# Endpoint to get accounts from all platforms
@app.route('/accounts')
def accounts():
    data = get_data()
    accounts = {}
    if "platforms" in data:
        for platform in data["platforms"]:
            platform_name = platform.get("value")
            if platform_name:
                accounts_data = get_accounts(platform_name)
                accounts[platform_name] = accounts_data
    return jsonify(accounts)

# Getting fields from an especific platform
def get_fields(platform):
    all_fields = []
    page = 1

    while True:
        url = f"{API_URL}/fields?platform={platform}&page={page}"
        headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            # Check if there are fields on actual page
            if "fields" in data and data["fields"]:
                all_fields.extend(data["fields"])
                page += 1
            else:
                break
        else:
            break
    
    return all_fields

# Endpoint to get fields from all platforms
@app.route('/fields')
def fields():
    platforms_data = get_data()
    all_fields = {}

    if "platforms" in platforms_data:
        for platform in platforms_data["platforms"]:
            platform_name = platform.get("value")
            if platform_name:
                fields_data = get_fields(platform_name)
                all_fields[platform_name] = fields_data
            
    return jsonify(all_fields)

# Getting insights from an especific account
def get_insights(platform, account_id, account_token, fields):
    all_insigths = []
    fields_str = ",".join(fields)
    url = f"{API_URL}/insights?platform={platform}&account={account_id}&token={account_token}&fields={fields_str}"
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        # Check if there are insights on actual page
        if "insights" in data and data["insights"]:
            all_insigths.extend(data["insights"])

    return all_insigths

# Endpoint to get insights from all accounts
@app.route('/insights')
def insights():
    platforms_data = get_data()
    all_insights = {}

    if "platforms" in platforms_data:
        for platform in platforms_data["platforms"]:
            platform_name = platform.get("value")
            if platform_name:
                # Getting platform accounts
                accounts_data = get_accounts(platform_name)
                # Getting platform fields
                fields_data = get_fields(platform_name)
                fields = [field["value"] for field in fields_data]

                # For each account, getting insights
                for account in accounts_data:
                    account_name = account.get("name")
                    account_id = account.get("id")
                    account_token = account.get("token")
                    if account_token:
                        insights_data = get_insights(platform_name, account_id, account_token, fields)
                        all_insights[f"{platform_name} - {account_name}"] = insights_data

    return jsonify(all_insights)

# Generating CSV from a especific platform
def generate_csv_platform(platfomrm):
    # Getting accounts
    accounts_data = get_accounts(platfomrm)
    # Getting fields from a platform
    fields_data = get_fields(platfomrm)
    fields = [field['value'] for field in fields_data]
    # All ads
    all_ads = []

    # For each account, getting insights
    for account in accounts_data:
        account_name = account.get("name")
        account_id = account.get("id")
        account_token = account.get("token")
        if account_id:
            insights_data = get_insights(platfomrm, account_id, account_token, fields)
        # Inserting the account name and platform name in each announcement
        for insight in insights_data:
            insight["account_name"] = account_name
            insight['platform'] = platfomrm
            all_ads.append(insight)
        # In case there aren't announcements
        if not all_ads:
            return Response("Sem dados disponíveis", mimetype='text/plain')
        
    return Response(generate_csv(all_ads), mimetype='csv')

# Generating CSV
def generate_csv(all_ads):
    header = list(all_ads[0].keys()) if all_ads else []
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=header, lineterminator='\n')
    writer.writeheader()
    for ad in all_ads:
        writer.writerow(ad)
    return output.getvalue()

# Endpoint to generate CSV from a especific platform
@app.route('/<platform>/')
def report_platform(platform):
    return generate_csv_platform(platform)

@app.route('/<platform>/resumo')
def report_platform_summary(platform):
    # Getting accounts 
    accounts_data = get_accounts(platform)
    fields_data = get_fields(platform)
    fields = [field['value'] for field in fields_data]
    aggregated_data = {}

    # For each account, getting insights
    for account in accounts_data:
        account_name = account.get("name")
        account_id = account.get("id")
        account_token = account.get("token")
        if account_id:
            insights_data = get_insights(platform, account_id, account_token, fields)
        # Aggregating data
        for insight in insights_data:
            if account_name not in aggregated_data:
                aggregated_data[account_name] = {
                    "Account Name": account_name,
                    "Platform": platform
                }
            for key, value in insight.items():
                if key not in ['Account Name', 'Platform']:
                    if isinstance(value, (int, float)) or value.isdigit():
                        aggregated_data[account_name][key] = 0
                    else:
                        aggregated_data[account_name][key] = ""
    
    for key, value in insight.items():
        if key not in ['Account Name', 'Platform']:
            if isinstance(value, (int, float)):
                aggregated_data[account_name][key] += value
        elif value.isdigit():
            aggregated_data[account_name][key] += int(value)

    summary_list = list(aggregated_data.values())

    csv_data = generate_csv(summary_list)

    return Response(csv_data, mimetype='csv')

@app.route('/geral')
def report_general():  
    platforms_data = get_data()
    all_ads = []
    all_fields = set()
    
    for platform in platforms_data['platforms']:
        platform_name = platform.get("value")
        if not platform_name:
            continue
        
        accounts_data = get_accounts(platform_name)
        fields_data = get_fields(platform_name)
        fields = [field["value"] for field in fields_data]
        
        all_fields.update(fields)
        
        for account in accounts_data:
            account_name = account.get("name")
            account_id = account.get("id")
            account_token = account.get("token")
            
            if account_id:
                insights_data = get_insights(platform_name, account_id, account_token, fields)
                
                for insight in insights_data:
                    insight["Account Name"] = account_name
                    insight["Platform"] = platform_name
                    
                    if platform_name == "ga4":
                        spend = float(insight.get("spend", 0))
                        clicks = int(insight.get("clicks", 0))
                        insight["Cost per Click"] = round(spend / clicks, 2) if clicks > 0 else 0
                    
                    all_ads.append(insight)
    
    all_fields.add("Account Name")
    all_fields.add("Platform")
    all_fields.add("Cost per Click")
    all_fields = sorted(list(all_fields)) 
    
    standardized_ads = []
    for ad in all_ads:
        standardized_ad = {field: ad.get(field, "") for field in all_fields}
        standardized_ads.append(standardized_ad)
    
    csv_data = generate_csv(standardized_ads)
    
    return Response(csv_data, mimetype="csv")

@app.route('/geral/resumo')
def report_general_summary():    
    platforms_data = get_data()
    aggregated_data = {}
    all_fields = set()

    for platform in platforms_data['platforms']:
        platform_name = platform.get("value")
        
        accounts_data = get_accounts(platform_name)
        fields_data = get_fields(platform_name)
        fields = [field["value"] for field in fields_data]
        
        all_fields.update(fields)
        
        for account in accounts_data:
            account_name = account.get("name")
            account_id = account.get("id")
            account_token = account.get("token")
            
            if account_id:
                insights_data = get_insights(platform_name, account_id, account_token, fields)
                
                for insight in insights_data:
                    if platform_name not in aggregated_data:
                        aggregated_data[platform_name] = {
                            "Platform": platform_name
                        }
                        for key, value in insight.items():
                            if key not in ["Account Name", "Platform"]:
                                if isinstance(value, (int, float)) or value.isdigit():
                                    aggregated_data[platform_name][key] = 0
                                else:
                                    aggregated_data[platform_name][key] = ""
                    
                    for key, value in insight.items():
                        if key not in ["Account Name", "Platform"]:
                            if isinstance(value, (int, float)):
                                aggregated_data[platform_name][key] += value
                            elif value.isdigit():
                                aggregated_data[platform_name][key] += int(value)
                    
                    if platform_name == "Google Analytics":
                        spend = aggregated_data[platform_name].get("spend", 0)
                        clicks = aggregated_data[platform_name].get("clicks", 0)
                        aggregated_data[platform_name]["Cost per Click"] = round(spend / clicks, 2) if clicks > 0 else 0
    
    all_fields.add("Platform")
    all_fields.add("Cost per Click")
    all_fields = sorted(list(all_fields)) 
    
    standardized_summary = []
    for platform, summary in aggregated_data.items():
        standardized_row = {field: summary.get(field, "") for field in all_fields}
        standardized_summary.append(standardized_row)
    
    csv_data = generate_csv(standardized_summary)
    
    return Response(csv_data, mimetype="csv")

if __name__ == '__main__':
    app.run(debug=True)
