_store = {}


class LarkUserStore:

    @staticmethod
    def add_user(user_id, user_data):
        _store[user_id] = user_data

    @staticmethod
    def get_user(user_id):
        return _store.get(user_id)

    @staticmethod
    def get_all_users():
        return _store

    @staticmethod
    def delete_user(user_id):
        if user_id in _store:
            del _store[user_id]
            return True
        return False
