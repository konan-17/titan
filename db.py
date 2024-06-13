import aiosqlite

class DatabaseUser:
    def __init__(self):
        self.db_path = "nation.db"
        self.conn = None

    async def get_connection(self):
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_path)
            await self.create_tables()
        return self.conn

    async def close_connection(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def create_tables(self):
        await self.create_table_users()
        await self.create_table_guild()
        await self.create_table_roles()
        await self.create_table_affairs()
        await self.create_table_tickets()
        await self.create_table_alerts()
        await self.create_table_id()

    async def create_table_users(self):
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    user_id INTEGER PRIMARY KEY,
                                    nation_id TEXT
                                  )''')
            await conn.commit()

    async def create_table_guild(self):
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS guild (
                                    guild_id INTEGER PRIMARY KEY,
                                    api TEXT,
                                    alliance_id TEXT,
                                    leader_role TEXT,
                                    offshore_id TEXT,
                                    offshore_role TEXT
                                  )''')
            await conn.commit()

    async def create_table_roles(self):
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS roles (
                                    guild_id INTEGER PRIMARY KEY,
                                    members TEXT
                                  )''')
            await conn.commit()

    async def create_table_affairs(self):
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS affairs (
                                    guild_id INTEGER PRIMARY KEY,
                                    internal TEXT,
                                    external TEXT,
                                    finance TEXT,
                                    military TEXT
                                  )''')
            await conn.commit()

    async def create_table_tickets(self):
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
                                    guild_id INTEGER PRIMARY KEY,
                                    category_id INTEGER,
                                    message TEXT
                                  )''')
            await conn.commit()

    async def create_table_alerts(self):
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
                                guild_id INTEGER PRIMARY KEY,
                                def_channel TEXT,
                                off_channel TEXT,
                                treaty TEXT
                              )''')
        await conn.commit()

    async def create_table_id(self):
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''CREATE TABLE IF NOT EXISTS ids (
                                nation_id TEXT PRIMARY KEY,
                                user_id INTEGER
                              )''')
            await conn.commit()


    async def add_user_nation(self, user_id, nation_id):
        if not isinstance(user_id, int) or not isinstance(nation_id, str):
            raise ValueError(f"Invalid types for user_id: {type(user_id)}, nation_id: {type(nation_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("INSERT INTO users (user_id, nation_id) VALUES (?, ?)", (user_id, nation_id))
            await conn.commit()

    async def is_user_registered(self, user_id):
        if not isinstance(user_id, int):
            raise ValueError(f"Invalid type for user_id: {type(user_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
            result = await cursor.fetchone()
        return result is not None

    async def remove_user(self, user_id):
        if not isinstance(user_id, int):
            raise ValueError(f"Invalid type for user_id: {type(user_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            await conn.commit()

    async def get_user_nation_id(self, user_id):
        if not isinstance(user_id, int):
            raise ValueError(f"Invalid type for user_id: {type(user_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT nation_id FROM users WHERE user_id=?", (user_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_api_key(self, guild_id, api):
        if not isinstance(guild_id, int) or not isinstance(api, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, api: {type(api)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO guild (guild_id, api) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET api=excluded.api''', (guild_id, api))
            await conn.commit()

    async def get_api_key(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT api FROM guild WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_alliance(self, guild_id, alliance_id):
        if not isinstance(guild_id, int) or not isinstance(alliance_id, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, alliance_id: {type(alliance_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO guild (guild_id, alliance_id) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET alliance_id=excluded.alliance_id''', (guild_id, alliance_id))
            await conn.commit()

    async def get_guild_alliance(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT alliance_id FROM guild WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_leader(self, guild_id, leader_role):
        if not isinstance(guild_id, int) or not isinstance(leader_role, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, leader_role: {type(leader_role)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO guild (guild_id, leader_role) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET leader_role=excluded.leader_role''', (guild_id, leader_role))
            await conn.commit()

    async def get_guild_leader(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT leader_role FROM guild WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_members(self, guild_id, members):
        if not isinstance(guild_id, int) or not isinstance(members, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, members: {type(members)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO roles (guild_id, members) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET members=excluded.members''', (guild_id, members))
            await conn.commit()

    async def get_guild_roles(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT members FROM roles WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return {"members": result[0]} if result else None

    async def add_guild_internal(self, guild_id, internal):
        if not isinstance(guild_id, int) or not isinstance(internal, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, internal: {type(internal)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO affairs (guild_id, internal) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET internal=excluded.internal''', (guild_id, internal))
            await conn.commit()

    async def get_guild_internal(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT internal FROM affairs WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_external(self, guild_id, external):
        if not isinstance(guild_id, int) or not isinstance(external, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, external: {type(external)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO affairs (guild_id, external) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET external=excluded.external''', (guild_id, external))
            await conn.commit()

    async def get_guild_external(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT external FROM affairs WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_finance(self, guild_id, finance):
        if not isinstance(guild_id, int) or not isinstance(finance, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, finance: {type(finance)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO affairs (guild_id, finance) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET finance=excluded.finance''', (guild_id, finance))
            await conn.commit()

    async def get_guild_finance(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT finance FROM affairs WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_military(self, guild_id, military):
        if not isinstance(guild_id, int) or not isinstance(military, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, military: {type(military)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO affairs (guild_id, military) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET military=excluded.military''', (guild_id, military))
            await conn.commit()

    async def get_guild_military(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT military FROM affairs WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_ticket_category(self, guild_id, category_id):
        if not isinstance(guild_id, int) or not isinstance(category_id, int):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, category_id: {type(category_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO tickets (guild_id, category_id) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET category_id=excluded.category_id''', (guild_id, category_id))
            await conn.commit()

    async def get_ticket_category(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT category_id FROM tickets WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_ticket_message(self, guild_id, message):
        if not isinstance(guild_id, int) or not isinstance(message, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, message: {type(message)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO tickets (guild_id, message) VALUES (?, ?)
                                    ON CONFLICT(guild_id) DO UPDATE SET message=excluded.message''', (guild_id, message))
            await conn.commit()

    async def get_ticket_message(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT message FROM tickets WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
        return result[0] if result else None

    async def add_guild_def_channel(self, guild_id, channel_id):
        if not isinstance(guild_id, int) or not isinstance(channel_id, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, channel_id: {type(channel_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO alerts (guild_id, def_channel) VALUES (?, ?)
                                ON CONFLICT(guild_id) DO UPDATE SET def_channel=excluded.def_channel''', (guild_id, channel_id))
        await conn.commit()

    async def get_guild_def_channel(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT def_channel FROM alerts WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def add_guild_off_channel(self, guild_id, channel_id):
        if not isinstance(guild_id, int) or not isinstance(channel_id, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, channel_id: {type(channel_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO alerts (guild_id, off_channel) VALUES (?, ?)
                                ON CONFLICT(guild_id) DO UPDATE SET off_channel=excluded.off_channel''', (guild_id, channel_id))
        await conn.commit()

    async def get_guild_off_channel(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT off_channel FROM alerts WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

    async def add_guild_treaty_channel(self, guild_id, channel_id):
        if not isinstance(guild_id, int) or not isinstance(channel_id, str):
            raise ValueError(f"Invalid types for guild_id: {type(guild_id)}, channel_id: {type(channel_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO alerts (guild_id, treaty_channel) VALUES (?, ?)
                                ON CONFLICT(guild_id) DO UPDATE SET treaty_channel=excluded.treaty_channel''', (guild_id, channel_id))
        await conn.commit()

    async def get_guild_treaty_channel(self, guild_id):
        if not isinstance(guild_id, int):
            raise ValueError(f"Invalid type for guild_id: {type(guild_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT treaty_channel FROM alerts WHERE guild_id=?", (guild_id,))
            result = await cursor.fetchone()
            return result[0] if result else None

     # Add user in id

    async def add_id_user(self, nation_id, user_id):
        if not isinstance(nation_id, str) or not isinstance(user_id, int):
            raise ValueError(f"Invalid types for nation_id: {type(nation_id)}, user_id: {type(user_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute('''INSERT INTO ids (nation_id, user_id) VALUES (?, ?)
                                    ON CONFLICT(nation_id) DO UPDATE SET user_id=excluded.user_id''', (nation_id, user_id))
            await conn.commit()

    async def get_id_user(self, nation_id):
        if not isinstance(nation_id, str):
            raise ValueError(f"Invalid type for nation_id: {type(nation_id)}")
        conn = await self.get_connection()
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT user_id FROM ids WHERE nation_id=?", (nation_id,))
            result = await cursor.fetchone()
            return result[0] if result else None