from sqlalchemy import create_engine, text

user = 'PI'
password = 'urubu100'   
host = 'localhost'
database = 'health_machine'

def get_engine():
    return create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

def get_sensor(modelo):
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id FROM sensor WHERE modelo = :modelo"), {'modelo': modelo})
        row = result.fetchone()
        if row:
            return row[0]
    return None
