import requests
import elementtree.ElementTree as ET

class BasecampError(Exception):
    pass

class Basecamp():

    def __init__(self, url, apikey):
        self.baseURL = url
        if self.baseURL[-1] == '/':
            self.baseURL = self.baseURL[:-1]
        
        self.auth = (apikey, 'X')
        
    def _request(self, path, data=None, put=False, post=False, delete=False, get=False):
        if isinstance(data, ET._ElementInterface):
            data = ET.tostring(data)
        url = self.baseURL + path
        headers = {'content-type': 'application/xml'}
        if post:
            answer = requests.post(url, data, auth=self.auth, headers=headers)
        elif put:
            if not data:
                headers['content-length'] = '0'
            answer = requests.put(url, data, auth=self.auth,headers=headers)
        elif delete:
            answer = requests.delete(url, auth=self.auth, headers=headers)
        else:
            answer = requests.get(url, auth=self.auth)
        
        if ( (post and answer.status_code != 201) or 
                (not post and answer.status_code != 200) ):
            self.last_error = answer.text
            raise BasecampError()
        return answer.text

    def get_last_error(self):
        return self.last_error

    # ---------------------------------------------------------------- #
    # General

    def company(self, company_id):
        """
        This will return the information for the referenced company.
        """
        path = '/companies/%u.xml' % company_id
        return self._request(path)
    
    def companies(self):
        """
        This will return a list of all companies visible to the 
        requesting user.
        """
        path = '/companies.xml' 
        return self._request(path)

    def companies_per_project(self, project_id):
        """
        This will return a list of all companies associated with the gieven 
        project.
        """
        path = '/companies/%u/companies.xml' % project_id
        return self._request(path)

    # ---------------------------------------------------------------- #
    # Categories 

    def file_categories(self, project_id):
        """
        This will return an alphabetical list of all file categories in the
        referenced project.
        """
        path = '/projects/%u/categories.xml?type=attachment' % project_id
        return self._request(path)

    def message_categories(self, project_id):
        """
        This will return an alphabetical list of all message categories in the
        referenced project.
        """
        path = '/projects/%u/categories.xml?type=post' % project_id
        return self._request(path)
    
    # ---------------------------------------------------------------- #
    # People 

    def me(self):
        """
        This will return the currently logged in person (you)
        """
        path = '/me.xml'
        return self._request(path)

    def people(self):
        """
        This will return all of the people visible to (and including) the
        requesting user.. 
        """
        path = '/people.xml'
        return self._request(path)


    def people_per_company(self, company_id):
        """
        This will return all of the people in the given company. 
        """
        path = '/companies/%u/people.xml' % company_id
        return self._request(path)

    def people_per_project(self, project_id):
        """
        This will return all of the people in the given project. 
        """
        path = '/projects/%u/people.xml' % project_id
        return self._request(path)

    def person(self, person_id):
        """
        This will return information about the referenced person.
        """
        path = '/people/%u.xml' % person_id
        return self._request(path)

    # ---------------------------------------------------------------- #
    # Projects 

    def projects(self):
        """
        This will return a list of all active, on-hold, and archived projects
        that you have access to. The list is not ordered.
        """
        path = '/projects.xml'
        return self._request(path)

    def project_count(self):
        """
        This will return a count of all projects, by project status. 
        If there are no projects with a particular status, that status entry
        will be omitted from the report
        """
        path = '/projects/count.xml'
        return self._request(path)

    def project(self, project_id):
        """
        This will return a single project identified by its integer ID
        """
        path = '/projects/%u.xml' % project_id
        return self._request(path)

    # ---------------------------------------------------------------- #
    # Messages

    def messages_per_project(self, project_id):
        """
        This will return the 25 most recent messages in the given project. 
        """
        path = '/projects/%u/posts.xml' % project_id
        return self._request(path)

    def messages_per_category(self, project_id, category_id):
        """
        This will return the 25 most recent messages in the given project 
        for the given category.
        """
        path = '/projects/%u/cat/%s/posts.xml' % (project_id, category_id)
        return self._request(path)

    def messages_archived(self, project_id):
        """
        This will return a summary for each message in the given project. 
        Note that a summary record includes only a few bits of 
        information about a messag, not the complete record.
        """
        path = '/projects/%u/posts/archive.xml' % project_id
        return self._request(path)

    def messages_archived_per_category(self, project_id, category_id):
        """
        This will return a summary for each message in the given project
        for the given category. Note that a summary record includes 
        only a few bits of information about a messag, 
        not the complete record.
        """
        path = '/projects/%u/cat/%s/posts/archive.xml' % (
                project_id, category_id)
        return self._request(path)

    def message(self, message_id):
        """
        This will return a single message record identified by its integer ID.
        """
        path = '/posts/%u.xml' % message_id
        return self._request(path)

    def _create_message_post_elem(self, category_id, title, body,
        private=False, notify=False):
        post = ET.Element('post')
        ET.SubElement(post, 'category-id').text = str(int(category_id))
        ET.SubElement(post, 'title').text = str(title)
        ET.SubElement(post, 'body').text = str(body)
        if notify:
            ET.SubElement(post, 'notify-about-changes').text = '1'
        #ET.SubElement(post, 'extended-body').text = str(extended_body)
        #if bool(use_textile):
        #    ET.SubElement(post, 'use-textile').text = '1'
        ET.SubElement(post, 'private').text = '1' if private else '0'
        return post

    def create_message(self, project_id, category_id, title, body,
        private=False, notify=None, attachments=None):
        """
        Creates a new message, optionally sending notifications to a selected
        list of people. Note that you can also upload files using this
        function, but you need to upload the files first and then attach them.
        See the description at the top of this document for more information.
        """
        path = '/projects/%u/posts.xml' % project_id
        req = ET.Element('request')
        req.append(self._create_message_post_elem(category_id, title, body,
            private))
        if notify:
            for person_id in notify:
                ET.SubElement(req, 'notify').text = str(int(person_id))
        # TODO: Implement attachments.
        if attachments is not None:
            raise NotSupportedErr('Attachments are currently not implemented.')
        ##for attachment in attachments:
        ##    attms = ET.SubElement(req, 'attachments')
        ##    if attachment['name']:
        ##        ET.SubElement(attms, 'name').text = str(attachment['name'])
        ##    file_ = ET.SubElement(attms, 'file')
        ##    ET.SubElement(file_, 'file').text = str(attachment['temp_id'])
        ##    ET.SubElement(file_, 'content-type').text \
        ##        = str(attachment['content_type'])
        ##    ET.SubElement(file_, 'original-filename').text \
        ##        = str(attachment['original_filename'])
        return self._request(path, req, post=True)

    def update_message(self, message_id, category_id, title, body,
        private=False, notify=None):
        """
        Updates an existing message, optionally sending notifications to a
        selected list of people. Note that you can also upload files using
        this function, but you have to format the request as
        multipart/form-data. (See the ruby Basecamp API wrapper for an example
        of how to do this.)
        """
        path = '/posts/%u.xml' % message_id
        req = ET.Element('request')
        req.append(self._create_message_post_elem(category_id, title, body,
            private, notify))
        if notify is not None:
            for person_id in notify:
                ET.SubElement(req, 'notify').text = str(int(person_id))
        return self._request(path, req, put=True)

    def delete_message(self, message_id):
        """
        Delete the specified message from the project.
        """
        path = '/posts/%u.xml' % message_id
        return self._request(path, delete=True)

    # ---------------------------------------------------------------- #
    # Comments

    def comments(self, resource, resource_id):
        """
        Return a list of the 50 most recent comments associated with 
        the specified resource, where the resource named in the URL 
        can be one of posts, milestones, or todo_items. For example, 
        to fetch the most recent comments for the todo item with an 
        id of 1, you would use the path: /todo_items/1/comments.xml. 
        """
        path = '/%s/%u/comments.xml' % (resource, resource_id)
        return self._request(path)

    def comment(self, comment_id):
        """
        Retrieve a specific comment by its id.
        """
        path = '/comments/%u.xml' % comment_id
        return self._request(path)

    def create_comment(self, resource, resource_id, body):
        """
        Create a new comment, associating it with a specific resource, 
        where the resource named in the URL can be one of posts, milestones, 
        or todo_items. For example, to create a comment for the milestone 
        with an ID of 1, you would use the path: /milestones/1/comments.xml.
        """
        path = '/%s/%u/comments.xml' % (resource, resource_id)
        #req = ET.Element('request')
        req = ET.Element('comment')
        #comment = ET.SubElement(req, 'comment')
        #ET.SubElement(comment, 'post-id').text = str(int(post_id))
        ET.SubElement(req, 'body').text = str(body)
        #ET.SubElement(comment, 'body').text = str(body)
        return self._request(path, req, post=True)

    def update_comment(self, comment_id, body):
        """
        Update a specific comment. This can be used to edit the content of an
        existing comment.
        """
        path = '/comments/%u.xml' % comment_id
        req = ET.Element('request')
        #ET.SubElement(req, 'comment_id').text = str(int(comment_id))
        comment = ET.SubElement(req, 'comment')
        ET.SubElement(comment, 'body').text = str(body)
        return self._request(path, req, put=True)

    def delete_comment(self, comment_id):
        """
        Delete the comment with the given id.
        """
        path = '/comments/%u.xml' % comment_id
        return self._request(path, delete=True)

    # ---------------------------------------------------------------- #
    # Lists

    def todo_lists(self, responsable_party=''):
        """
        Returns a list of todo-list records, with todo-item records that 
        are assigned to the given "responsible party". If no responsible 
        party is given, the current user is assumed to be the responsible 
        party. The responsible party may be changed by setting the 
        "responsible_party" query parameter to a blank string 
        (for unassigned items), a person-id, or a company-id prefixed by 
        a "c" (e.g., c1234).
        """
        path = '/todo_lists.xml?responsible_party=%u' % responsable_party
        return self._request(path)

    def todo_lists_per_project(self, project_id, filter):
        """
        Returns a list of todo-list records that are in the given project. 
        By default, all lists are returned, but you can filter the result 
        by giving the "filter" query parameter, set to "all" (the default), 
        "pending" (for lists with uncompleted items), and "finished" 
        (for lists that have no uncompleted items). The lists will be returned 
        in priority order, as determined by their ordering. 
        (See the "reorder lists" action.)
        """
        path = '/projects/%u/todo_lists.xml?filter=%s' % (project_id, filter)
        return self._request(path)

    def todo_list(self, list_id):
        """
        This will return the metadata and items for a specific list.
        """
        path = '/todo_lists/%u.xml' % list_id
        return self._request(path)

    def create_todo_list(self, project_id, milestone_id=None, private=None,
        tracked=False, name=None, description=None, template_id=None):
        """
        This will create a new, empty list. You can create the list
        explicitly, or by giving it a list template id to base the new list
        off of.
        """
        path = '/projects/%u/todo_lists.xml' % project_id
        req = ET.Element('todo-list')
        if milestone_id is not None:
            ET.SubElement(req, 'milestone-id').text = str(milestone_id)
        if private is not None:
            ET.SubElement(req, 'private').text = str(bool(private)).lower()
        ET.SubElement(req, 'tracked').text = str(bool(tracked)).lower()
        if name is not None:
            ET.SubElement(req, 'name').text = str(name)
            ET.SubElement(req, 'description').text = str(description)
        if template_id is not None:
            ET.SubElement(req, 'todo-list-template-id').text = str(int(template_id))
        return self._request(path, req, post=True)

    def update_todo_list(self, list_id, name, description, milestone_id=None,
        private=None, tracked=None):
        """
        With this call you can alter the metadata for a list.
        """
        path = '/todo_lists/%u.xml' % list_id
        req = ET.Element('todo-list')
        ET.SubElement(req, 'name').text = str(name)
        ET.SubElement(req, 'description').text = str(description)
        if milestone_id is not None:
            ET.SubElement(req, 'milestone_id').text = str(int(milestone_id))
        if private is not None:
            ET.SubElement(req, 'private').text = str(bool(private)).lower()
        if tracked is not None:
            ET.SubElement(req, 'tracked').text = str(bool(tracked)).lower()
        return self._request(path, req, put=True)

    def delete_todo_list(self, list_id):
        """
        This call will delete the entire referenced list and all items
        associated with it. Use it with caution, because a deleted list cannot
        be restored!
        """
        path = '/todo_lists/%u.xml' % list_id
        return self._request(path, delete=True)

    # ---------------------------------------------------------------- #
    # Items

    def items(self, list_id):
        """
        Returns all todo item records for a single todo list. This is almost 
        the same as the "Get list" action, except it does not return any 
        information about the list itself. The items are returned in priority 
        order, as defined by how they were ordered either in the web UI, or 
        via the "Reorder items" action.
        """
        path = '/todo_lists/%u/todo_items.xml' % list_id
        return self._request(path)

    def item(self, item_id):
        """
        Returns a single todo item record, given its integer ID.
        """
        path = '/todo_items/%u.xml' % item_id
        return self._request(path)

    def complete_todo_item(self, item_id):
        """
        Marks the specified item as "complete". If the item is already
        completed, this does nothing.
        """
        path = '/todo_items/%u/complete.xml' % item_id
        return self._request(path, put=True)

    def uncomplete_todo_item(self, item_id):
        """
        Marks the specified item as "uncomplete". If the item is already
        uncompleted, this does nothing.
        """
        path = '/todo_items/%u/uncomplete.xml' % item_id
        return self._request(path, put=True)

    def create_todo_item(self, list_id, content, party_id=None, notify=False,
            due_at=None):
        """
        Creates a new todo item record for the given list. The new record 
        begins its life in the "uncompleted" state. (See the "Complete" and 
        "Uncomplete" actions.) It is added at the bottom of the given list. 
        If a person is responsible for the item, give their id as the party_id 
        value. If a company is responsible, prefix their company id with a 'c' 
        and use that as the party_id value. If the item has a person as the 
        responsible party, you can also use the "notify" key to indicate 
        whether an email should be sent to that person to tell them about the 
        assignment.
        """
        path = '/todo_lists/%u/todo_items.xml' % list_id
        req = ET.Element('todo-item')
        ET.SubElement(req, 'content').text = str(content)
        if party_id :
            ET.SubElement(req, 'responsible-party').text = str(party_id)
            ET.SubElement(req, 'notify').text = str(bool(notify)).lower()
        if due_at:
            ET.SubElement(req, 'due-at').text = str(due_at)
        return self._request(path, req, post=True)

    def update_todo_item(self, item_id, content, party_id=None, notify=False):
        """
        Modifies an existing item. The values work much like the "create item"
        operation, so you should refer to that for a more detailed explanation.
        """
        path = '/todo_items/%u.xml' % item_id
        req = ET.Element('todo-item')
        ET.SubElement(req, 'content').text = str(content)
        if party_id is not None:
            ET.SubElement(req, 'responsible-party').text = str(party_id)
            ET.SubElement(req, 'notify').text = str(bool(notify)).lower()
        return self._request(path, req, put=True)

    def delete_todo_item(self, item_id):
        """
        Deletes the specified item, removing it from its parent list.
        """
        path = '/todo_items/%u.xml' % item_id
        return self._request(path, delete=True)

    # ---------------------------------------------------------------- #
    # Time Entry 

    def time_entries_per_project(self, project_id, page=None):
        """
        Returns a page full of time entries for the given project, 
        in descending order by date. Each page contains up to 50 time entry 
        records. To select a different page of data, set the "page" query 
        parameter to a value greater than zero. The X-Records HTTP header 
        will be set to the total number of time entries in the project, 
        X-Pages will be set to the total number of pages, and X-Page will be 
        set to the current page.
        """
        if page:
            path = '/projects/%u/time_entries.xml?page=%u' % (project_id, page)
        else: 
            path = '/projects/%u/time_entries.xml' % project_id
        return self._request(path)

    def time_entries_per_todo_item(self, todo_item_id):
        """
        Returns all time entries associated with the given todo item, 
        in descending order by date.
        """
        path = '/todo_items/%u/time_entries.xml' % todo_item_id
        return self._request(path)

    def time_entry(self, time_entry_id):
        """
        Retrieves a single time-entry record, given its integer ID.
        """
        path = '/time_entries/%u.xml' % time_entry_id
        return self._request(path)

    def create_time_entry(self, description, hours, person_id, 
            entry_date=None, project_id=None, todo_item_id=None):
        """
        Creates a new time entry for the given project. If todo_item_id is
        not None creates a new time entry for the given todo item.
        """
        if todo_item_id:
            path = '/todo_items/%u/time_entries.xml' % todo_item_id 
        elif project_id:
            path = '/projects/%u/time_entries.xml' % project_id
        else: 
            return ""
        req = ET.Element('time-entry')
        ET.SubElement(req, 'description').text = str(description)
        ET.SubElement(req, 'person-id').text = str(person_id)
        ET.SubElement(req, 'hours').text = str(hours)
        if entry_date:
            ET.SubElement(req, 'date').text = str(entry_date)
        return self._request(path, req, post=True)

    def update_time_entry(self, time_entry_id, description, hours, 
            person_id, entry_date=None, todo_item_id=None):
        """
        Updates the given time-entry record with the data given.
        """
        path = '/time_entries/%u.xml' % time_entry_id
        req = ET.Element('time-entry')
        ET.SubElement(req, 'description').text = str(description)
        ET.SubElement(req, 'person-id').text = str(person_id)
        ET.SubElement(req, 'hours').text = str(hours)
        if entry_date:
            ET.SubElement(req, 'date').text = str(entry_date)
        if todo_item_id:
            ET.SubElement(req, 'todo-item-id').text = str(todo_item_id)
        return self._request(path, req, put=True)

    def delete_todo_item(self, time_entry_id):
        """
        Destroys the given time entry record.
        """
        path = '/time_entries/%u.xml' % item_id
        return self._request(path, delete=True)

