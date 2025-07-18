
#Checks if an item is a blueprint based on name (Refactor to check against API db later?)
def get_blueprint_status(item):
    if str.lower("Blueprint") not in item.split():
        return False
    else:
        return True

def get_set_status(item):

    pass

def get_set_count(item):
    pass

def get_item_id(item):
    pass

def get_item_value(item):
    pass

