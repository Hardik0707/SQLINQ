from moz_sql_parser import parse
import json
import sys

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('./main/logs/application.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 


# Global variables
SelectValue = ''
FromValue = ''
WhereValue=''
OrderByValue = ''
GroupByValue = ''
RangeVariableName = 'range'
IsInnerJoin = False

# Sign creator function
def OperatorToSign(operator):
  global IsInnerJoin
  Operators = {
    'eq':'==',
    'neq':'!=',
    'gt':'>',
    'lt':'<',
    'gte':'<=',
    'lte':'<=',
    'and':'and',
    'or':'or'
  }
  if IsInnerJoin == True and operator == 'eq':
    return 'equals'
  return Operators[operator]


# Select Function

def SelectValueSet(select):
  list_len = 0
  global RangeVariableName
  if type(select) is str:
    SelectValue = 'select '+RangeVariableName+';'
  elif type(select) is list:
    SelectValue = 'select new { \n'
    for i in select:
      if list_len == (len(select)-1):
        SelectValue = SelectValue + RangeVariableName+'.'+i['value']+'\n'
      else:
        SelectValue = SelectValue + RangeVariableName+'.'+i['value']+',\n'
      list_len = list_len + 1
    SelectValue = SelectValue + '};'
  return SelectValue

# From Function with join 
def FromValueSet(fromVal):
  FromValue = ''
  global RangeVariableName,IsInnerJoin
  
  #if only one table  
  if type(fromVal) is str:
    FromValue = 'from '+RangeVariableName+' in '+fromVal
  
  # if one table with alias name
  elif type(fromVal) is dict:
    FromValue = 'from ' + fromVal['name'] + ' in '+ fromVal['value']   

  # if multiple table 
  elif type(fromVal) is list:
    for i in fromVal:
      if type(i) is str:
        FromValue = FromValue + 'from '+ i +' in '+ i

      elif type(i) is dict:

        # Check inner join is present or not
        if i.get('inner join') != None:     #present inner join
          join = i['inner join']
          on = i['on']

          # Set INNER JOIN Present
          IsInnerJoin=True
          
          if type(join) == str:
            FromValue = FromValue + '\n' + 'join '+ join +' in '+ join + '\non ' + WhereClause(on)
          else:
            FromValue = FromValue + '\n' + 'join '+ join["name"]+' in '+ join["value"] + '\non ' + WhereClause(on)
          
          IsInnerJoin = False  
        
        else:
          FromValue = FromValue + 'from '+ i["name"]+' in '+ i["value"]
  
  return FromValue

# Where Clause Function
def WhereValueSet(where_value):
  result = 'where ' + WhereClause(where_value)
  return result

def WhereClause(where_value):       #Parameter should be dict type
   operator = list(where_value.keys())[0]
   global RangeVariableName
   operands = where_value[operator]
   operand1 = operands[0]
   operand2 = operands[1]

   if type(operand1) is dict:
     operand1 = '( '+WhereClause(operand1)
   elif type(operand1) is str:
     if IsInnerJoin == True:
       operand1 = str(operand1)
     else:
       operand1 = RangeVariableName+'.'+str(operand1)

   if type(operand2) is dict:
     operand2 = WhereClause(operand2) + ')'
   
   # Create condition string 
   result = str(operand1) + ' ' + OperatorToSign(operator) + ' ' + str(operand2)
   return result

# GroupBy Clause Function
def GroupByValueSet(groupby_value):
  global RangeVariableName
  result = 'group ' + RangeVariableName + ' by ' + GroupByClause(groupby_value)
  return result

def GroupByClause(groupby_value):
  list_len = 0
  global RangeVariableName
  result = ''
  if type(groupby_value) is dict:
    result = result + RangeVariableName+'.'+groupby_value['value'] 
  elif type(groupby_value) is list:
    for i in groupby_value:
      if list_len == (len(groupby_value)-1):
        result = result +RangeVariableName+'.'+i['value']
      else:
        result = result +RangeVariableName+'.'+i['value']+','
      list_len = list_len + 1
  return result

# OrderBy Clause Function
def OrderByValueSet(orderby_value):
  result = 'orderby ' + OrderByClause(orderby_value)
  return result

def OrderByClause(orderby_value):
  list_len = 0
  SortType = {'asc' : 'ascending', 'desc': 'descending'}
  result = ''
  if type(orderby_value) is dict:
    result = result + RangeVariableName+'.'+orderby_value['value'] 
    if orderby_value.get('sort') != None:
       result = result + ' ' + SortType[orderby_value['sort']]
  elif type(orderby_value) is list:
    for i in orderby_value:
      if list_len == (len(orderby_value)-1):
        result = result +RangeVariableName+'.'+i['value']
      else:
        result = result +RangeVariableName+'.'+i['value']+','
      list_len = list_len + 1
  return result

# SQLINQ Converter

def SQLINQConverter(values):
  global RangeVariableName,SelectValue,FromValue,WhereValue,OrderByValue,GroupByValue

  # Setting Select Keyword values
  SelectValue = '\n' + SelectValueSet(values['select'])
  
  # Setting From Keyword values
  FromValue = FromValueSet(values['from'])

  # Setting Where Keyword values (Optional)
  if values.get('where')!= None:
    WhereValue = '\n' + WhereValueSet(values['where'])

  #Setting OrderBy Keyword values (Optional)
  if values.get('orderby') != None:
    OrderByValue = '\n' + OrderByValueSet(values['orderby'])

  #Setting OrderBy Keyword values (Optional)
  if values.get('groupby') != None:
    GroupByValue = '\n' + GroupByValueSet(values['groupby'])

  result = FromValue + WhereValue +  GroupByValue + OrderByValue + SelectValue
  return result

# Main Convert Function

def Convert(query):
    try:
      # Replace single quote with double quotes 
      query = query.replace("'","\"")
      parsed_query = parse(query)
      return SQLINQConverter(parsed_query)
    except:
      # Log an error message
      logger.error(sys.exc_info())
      return "Invalid Query"