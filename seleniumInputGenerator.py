import json
from datetime import datetime
import pandas as pd

def transform_json(data):
    transformed_data = data
    return transformed_data

def collect_rule_data(rules_dict):

    new_dict = {}

    for column in rules_dict.keys():
        if(column == 'Rule'):
            for rules in rules_dict[column]:
                rule_identifier=rules['Rule Identifier(guid)']
                if rule_identifier in new_dict:
                    print('rule is already there please check the sheet')
                else:
                    new_dict[rule_identifier]={'Name':rules['Rule Name'],'Description':rules['Description'],'StartDate':rules['Start Date and Time'],'Status':rules['Status'],'RuleScope':rules['Rule Scope'],'Product':rules['Product'],'Parent Conditions':{},'Child Conditions':{},'ActionJSON':{}}

        if(column == 'Conditions'):
            
            for condition in rules_dict[column]:

                condition_rule_identifier=condition['Rule Identifier(guid)']
                condition_identifier=condition['Condition Identifier(guid)']

                if condition_rule_identifier in new_dict:

                    if pd.isna(condition.get("Parent Condition", None)):
                        new_dict[condition_rule_identifier]['Parent Conditions'][condition_identifier]=condition
                    else:
                        parent_condition=condition['Parent Condition']
                        if parent_condition not in new_dict[condition_rule_identifier]['Child Conditions']:
                            new_dict[condition_rule_identifier]['Child Conditions'][parent_condition]=[condition]
                        else:
                            new_dict[condition_rule_identifier]['Child Conditions'][parent_condition].append(condition)

        if(column == 'Actions'):
            
            for action in rules_dict[column]:
                action_rule_identifier=action['Rule Identifier(guid)']
                if action_rule_identifier in new_dict:
                    
                    parent_action_name=action['Parent Action']

                    if parent_action_name not in new_dict[action_rule_identifier]['ActionJSON']:
                        new_dict[action_rule_identifier]['ActionJSON'][parent_action_name]=[action]
                    else:
                        new_dict[action_rule_identifier]['ActionJSON'][parent_action_name].append(action)
                                

    return new_dict

def generateSeleniumInputJSON(rule_JSON):

    

    for ruleIdentifier in rule_JSON.keys():

        #date conversiom
        date_str=rule_JSON[ruleIdentifier]['StartDate']
        date_obj = datetime.strptime(date_str, "%m/%d/%Y, %I:%M %p")
        formatted_date = date_obj.strftime("%b %d, %Y")
        rule_JSON[ruleIdentifier]['StartDate']=formatted_date

        #rule_condition=rule_JSON[ruleIdentifier]['Conditions']

        condition_JSON={}
        if(rule_JSON[ruleIdentifier]['RuleScope']=='Bundle'):
            condition_JSON['Product']=rule_JSON[ruleIdentifier]['Product']

        condition_JSON['Conditional Operator']='AND'
        if(len(rule_JSON[ruleIdentifier]['Parent Conditions'])>0):
            #print('parent conditions are more than 1')
            condition_JSON['Conditions']=[]
            for parent_condition in rule_JSON[ruleIdentifier]['Parent Conditions'].keys():
                new_parent_condition={}
                new_parent_condition['Condition Identifier']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Condition Identifier(guid)']
                new_parent_condition['Sequence']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Sequence']
                new_parent_condition['Type']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Type']


                if(rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Type']== 'Resource'):
                    new_parent_condition['Resource']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Resource/Field/Attribute']
                if(rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Type']== 'Attribute'):
                    new_parent_condition['AttributeName']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Resource/Field/Attribute']
                if(rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Type']== 'Field'):
                    new_parent_condition['Field']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Resource/Field/Attribute']

                
                new_parent_condition['Operator']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Operator']
                new_parent_condition['Value']=rule_JSON[ruleIdentifier]['Parent Conditions'][parent_condition]['Value']
                new_parent_condition['Conditional Operator']='AND'

                child_condition_List=rule_JSON[ruleIdentifier]['Child Conditions'][parent_condition]

                new_parent_condition['SubConditions']=[]
                for child_cond in child_condition_List:
                    new_sub_condition={}
                    new_sub_condition['Condition Identifier']=child_cond['Condition Identifier(guid)']
                    new_sub_condition['Sequence']=child_cond['Sequence']
                    new_sub_condition['Type']=child_cond['Type']
                    if(child_cond['Type'] == 'Attribute'):
                        new_sub_condition['AttributeName']=child_cond['Resource/Field/Attribute']
                    if(child_cond['Type'] == 'Field'):
                        new_sub_condition['Field']=child_cond['Resource/Field/Attribute']
                    new_sub_condition['Operator']=child_cond['Operator']
                    new_sub_condition['Value']=child_cond['Value']
                    new_parent_condition['SubConditions'].append(new_sub_condition)



                condition_JSON['Conditions'].append(new_parent_condition)
            
        else:
            print('parent conditions are less than 1')
            condition_JSON['Conditions']=[]

        rule_JSON[ruleIdentifier]['Condition']=condition_JSON
        del rule_JSON[ruleIdentifier]['Parent Conditions']
        del rule_JSON[ruleIdentifier]['Child Conditions']

        if(len(rule_JSON[ruleIdentifier]['ActionJSON'])>0):
            #print('more than one action')
            new_action_json={'Actions':[]}
            for actionName in rule_JSON[ruleIdentifier]['ActionJSON'].keys():
                print('actionName=>',actionName)
                print('actionName list=>',rule_JSON[ruleIdentifier]['ActionJSON'][actionName])  
                new_action={}
                new_action['Action']=rule_JSON[ruleIdentifier]['ActionJSON'][actionName][0]['Action']
                new_action['Product']=rule_JSON[ruleIdentifier]['ActionJSON'][actionName][0]['Product']
                new_action['MsgType']=rule_JSON[ruleIdentifier]['ActionJSON'][actionName][0]['Message Type']
                new_action['Msg']=rule_JSON[ruleIdentifier]['ActionJSON'][actionName][0]['Message']
                new_action['Action Name']=actionName
                new_action['SubActions']=[]
                print('new_action=>',new_action)
                for sub_action in rule_JSON[ruleIdentifier]['ActionJSON'][actionName]:
                    print('sub_action=>',sub_action)
                    new_sub_action={}
                    new_sub_action['Action Identifier']=sub_action['Actions Identifier(guid)']
                    new_sub_action['Product']=sub_action['Product']
                    sub_action_att=sub_action['Attribute']
                    print('sub_action_att=>',sub_action_att)
                    if pd.isna(sub_action.get("Attribute", None)):
                        print('is action att NAN=>')
                        new_sub_action['Type']=None
                    else:
                        new_sub_action['Type']='Attribute'

                    
                    new_sub_action['Operator']=sub_action['Operator']
                    new_sub_action['Value']=sub_action['Value']
                    new_sub_action['Parent Action Name']=actionName
                    # new_sub_action['Sequence']=sub_action['Sequence']
                    new_action['SubActions'].append(new_sub_action)
                new_action_json['Actions'].append(new_action)
            rule_JSON[ruleIdentifier]['Action']=new_action_json
            del rule_JSON[ruleIdentifier]['ActionJSON']
    return rule_JSON

    


def main(data, output_file):

    transformed_data = transform_json(data)

    rule_JSON=collect_rule_data(transformed_data)

    final_selenium_input=generateSeleniumInputJSON(rule_JSON)
    json_data = json.dumps(final_selenium_input, indent=4)
    print('final_selenium_input===========>',json_data)
    return final_selenium_input





# Ensures script runs only when executed directly
if __name__ == "__main__":
    print("❌ No input data provided! This script is meant to be called from another script.")
