#    Coding: utf-8

#    py-activiti - Python Wrapper For Activiti BPMN2.0 API
#    Copyright (C) 2011  xtensive.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>


from activiti import call_service
from string import lower
from urllib2 import HTTPError
    
    
#------------------------------------------------------------------------------
# ACTIVITI REPOSITORY API
# @version: 1.0
#------------------------------------------------------------------------------       
def activiti_deployment_upload(username, password, deploy_file, cb_success='success', cb_failure='failure', debug=False):
    '''
    TODO: Why returning HTML ??? why not returning simple JSON and decide after what to do with the result ?? 
    '''
    _data = {'deployment': deploy_file, 'success': cb_success, 'failure': cb_failure}
    return call_service('deployment', username, password, debug, _data, method='POST', is_multipart=True)
    

def activiti_deployments(username, password, debug=False):
    '''
    '''
    json_data = call_service('deployments', username, password, debug)
    return json_data['data']


def activiti_deployment_resource(username, password, deploy_id, resource_name, debug=False):
    '''
    FIXME: an API to retrieve resources bound to a repository is missing
    FIXME: the java class for resource retrieval is missing ???
    '''
    return call_service('deployment/%s/resource/%s' % (deploy_id, resource_name), username, password, debug)


def activiti_deployment_delete(username, password, deploy_id, cascade=False, debug=False):
    '''
    '''
    try:
        json_data = call_service('deployment/%s?cascade=%s' % (deploy_id, lower(str(cascade))), username, password, debug, method='DELETE')
        return json_data['success']
    except Exception:
        return False
    
    
    
def activiti_deployments_delete(username, password, deploy_ids, cascade=False, debug=False):
    '''
    @param deploy_ids: List of deployment ids
    FIXME: bug at the API level /deployments/delete
    FIXME: problem got a 405 not authorized method using POST
    '''
    data = {'deploymentIds': deploy_ids}
    json_data = call_service('deployments/delete?cascade=%s' % lower(str(cascade)), username, password, debug, data, method='POST')
    return json_data
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# ACTIVITI ENGINE API
# @version: 1.0
#------------------------------------------------------------------------------       
def activiti_process_engine(username, password, debug=False):
    '''
    '''
    json_data = call_service('process-engine', username, password, debug)
    return json_data
#------------------------------------------------------------------------------ 

#------------------------------------------------------------------------------
# ACTIVITI PROCESSES API
# @version: 1.0
#------------------------------------------------------------------------------       
def activiti_process_definitions(username, password, debug=False):
    '''
    '''
    json_data = call_service('process-definitions', username, password, debug)
    return json_data['data']


def activiti_process_definition(username, password, process_id, debug=False):
    '''
    FIXME: no router exists for the service and java class is missing
    '''
    json_data = call_service('process-definition/%s' % process_id, username, password, debug)
    return json_data


def activiti_process_definition_form(username, password, process_id, format='json', debug=False):
    '''
    FIXME: the form does not exist in the diagram. 
    '''
    return call_service('process-definition/%s/form?format=%s' % (process_id, format), username, password, debug)


def activiti_process_instance(username, password, procdef_id=None, procdef_key=None, debug=False, **forms):
    '''
    Start a new process instance from the given process definition id or the process definition key.
    '''
    _data = {'businessKey': ''}
    if procdef_key:
        _data['processDefinitionKey'] = procdef_key
    elif procdef_id:
        _data['processDefinitionId'] = procdef_id
    else:
        raise Exception('Process Definition Id and Process Definition Key could not be None')
    return call_service('process-instance', username, password, debug=debug, data=_data, method='POST')


def activiti_process_instances(username, password, business_key=None, proc_def_id=None, debug=False):
    '''
    '''
    _service = 'process-instances'
    if business_key:
        _service += '?businessKey=%s' % business_key
    elif proc_def_id:
        _service += '?processDefinitionId=%s' % proc_def_id
    json_data = call_service(_service, username, password, debug)
    return json_data['data']


def activiti_process_instance_diagram(username, password, process_id, debug=False):
    '''
    '''
    return call_service('processInstance/%s/diagram' % process_id, username, password, debug)
#------------------------------------------------------------------------------
    
#------------------------------------------------------------------------------
# ACTIVITI IDENTITY API
# @version: 1.0
#------------------------------------------------------------------------------       
def activiti_login(username, password, debug=False):
    '''
    '''
    json_data = call_service('login', debug=debug, data={"userId": username, "password": password})
    return json_data
    
    
def activiti_user_info(username, password, debug=False):
    '''
    '''
    json_data = call_service('user/%s' % username, username, password, debug)
    return json_data


def activiti_user_groups(username, password, debug=False):
    json_data = call_service('user/%s/groups' % username, username, password, debug)
    return json_data['data']


def activiti_group(username, password, groupid, debug=False):
    '''
    '''
    json_data = call_service('group/%s' % groupid, username, password, debug)
    return json_data


def activiti_group_users(username, password, group_id, debug=False):
    '''
    '''
    json_data = call_service('groups/%s/users' % group_id, username, password, debug)
    return json_data['data']
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# ACTIVITI TASKS API
# @version: 1.0
#------------------------------------------------------------------------------
def activiti_tasks_assignee(username, password, user_id=None, debug=False):
    '''
    Require authentication
    [PASSED]
    '''
    if user_id is None:
        user_id = username
    json_data = call_service('tasks?assignee=%s' % user_id, username, password, debug)
    return json_data['data']


def activiti_tasks_candidate(username, password, user_id=None, debug=False):
    '''
    [PASSED]
    '''
    if user_id is None:
        user_id = username
    json_data = call_service('tasks?candidate=%s' % user_id, username, password, debug)
    return json_data['data']


def activiti_tasks_group(username, password, groupname, debug=False):
    '''
    [PASSED]
    '''
    json_data = call_service('tasks?candidate-group=%s' % groupname, username, password, debug)
    return json_data['data']


def activiti_task(username, password, task_id, debug=False):
    '''
    [PASSED]
    '''
    json_data = call_service('task/%s' % task_id, username, password, debug)
    return json_data


def activiti_tasks_summary(username, password, user_id=None, debug=False):
    '''
    [PASSED]
    '''
    if user_id is None:
        user_id = username
    json_data = call_service('tasks-summary?user=%s' % user_id, username, password, debug)
    return json_data


def activiti_task_form_properties(username, password, task_id, debug=False):
    '''
    '''
    json_data = call_service('form/%s/properties' % task_id, username, password, debug)    
    return json_data


def activiti_task_form(username, password, task_id, debug=False):
    '''
    TO BE TESTED ???
    '''
    try:
        call_service('task/%s/form' % task_id, username, password, debug)
    except HTTPError as e:
        #FIXME: better error handling
        return None


def activiti_task_claim(username, password, task_id, debug=False):
    '''
    '''
    try:
        json_data = call_service('task/%s/claim' % task_id, username, password, debug, data={}, method='PUT')
        _result = json_data['success']
    except:
        return False
    return True


def activiti_task_complete(username, password, task_id, data, debug=False):
    '''
    '''
    json_data = call_service('task/%s/complete' % task_id, username, password, debug, data=data, method='PUT')
    return json_data
#------------------------------------------------------------------------------    

#------------------------------------------------------------------------------
# ACTIVITI MANAGEMENT API
# @version: 1.0
#------------------------------------------------------------------------------
def activiti_job_list(username, password, debug=False):
    '''
    '''
    json_data = call_service('management/jobs', username, password, debug)
    return json_data['data']


def activiti_job(username, password, job_id, debug=False):
    '''
    '''
    json_data = call_service('management/job/%s' % job_id, username, password, debug)
    return json_data


def activiti_job_execute(username, password, job_id, debug=False):
    '''
    '''
    json_data = call_service('management/job/%s/execute' % job_id, username, password, debug, 'PUT')
    return json_data


def activiti_jobs_execute(username, password, job_ids, debug=False):
    '''
    @param job_ids: List of job ids 
    '''
    data = {'jobIds': job_ids}
    json_data = call_service('management/jobs/execute', username, password, debug, data)
    return json_data


def activiti_tables(username, password, debug=False):
    '''
    '''
    json_data = call_service('management/tables', username, password, debug)
    return json_data['data']


def activiti_table_metadata(username, password, table_name, debug=False):
    '''
    '''
    json_data = call_service('management/table/%s' % table_name, username, password, debug)
    return json_data


def activiti_table_data(username, password, table_name, debug=False):
    json_data = call_service('management/table/%s/data' % table_name, username, password, debug)
    return json_data['data']
#------------------------------------------------------------------------------