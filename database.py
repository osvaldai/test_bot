import sqlite3


class SQLighter:

    def __init__(self, database, name_table):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.name_table = name_table
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def number_events(self):
        """get number of events"""
        with self.connection:
            return self.cursor.execute(
                "SELECT COUNT(*) FROM %(name_table)s WHERE id" % {'name_table': self.name_table},
            ).fetchone()


    def del_row(self, ids):
        """del rows on database"""
        with self.connection:
            return self.cursor.execute(
                "DELETE FROM %(name_table)s WHERE id = %(id)s" % {'name_table': self.name_table, 'id': ids},
            )


    def get_devs(self, ids):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            return self.cursor.execute(
                "SELECT * FROM %(name_table)s ORDER BY id = %(limit)s" % {'name_table': self.name_table,
                                                                                   'limit': ids}).fetchone()


    def add_devs(self, name, title, description, dt):
        """Добавляем новое событие"""
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO %(name_table)s (name, title, description, dt) VALUES(?,?,?,?)" % {'name_table': self.name_table},
                (name, title, description, dt))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
