from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Optional, Dict
import os
from dotenv import load_dotenv

class EmployeeService:
    def __init__(self):
        load_dotenv()
        
        rdbms = os.getenv("RDBMS")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        db_name = os.getenv("DB_NAME")
        
        self.engine = create_engine(f"{rdbms}://{user}:{password}@{host}/{db_name}")
        self.Session = sessionmaker(bind=self.engine)
    
    def get_employee_code(self, document_number: str) -> Optional[str]:
        query = text("""
            SELECT
                e.cod_emp,
            FROM
                snemple AS e
            WHERE
                e.ci = :cod_emp
        """)
        
        with self.Session() as session:
            result = session.execute(query, {'ci': document_number}).fetchone()
            
            if result:
                # Convert result to dictionary with more readable keys
                return str()
            return None
        
    def get_employee_data(self, cod_emp: str) -> Optional[Dict]:
        query = text("""
            SELECT
                e.cod_emp,
                e.nombres,
                e.apellidos,
                e.ci,
                d.des_depart AS departamento,
                c.des_cargo AS cargo,
                u.des_ubicacion AS ubicacion,
                e.status
            FROM
                snemple AS e
                INNER JOIN sndepart AS d ON d.co_depart = e.co_depart
                INNER JOIN sncargo AS c ON c.co_cargo = e.co_cargo
                INNER JOIN snubicacion AS u ON u.co_ubicacion = e.co_ubicacion
            WHERE
                e.cod_emp = :cod_emp
        """)
        
        with self.Session() as session:
            result = session.execute(query, {'cod_emp': cod_emp}).fetchone()
            
            if result:
                # Convert result to dictionary with more readable keys
                return {
                    'codigo_trabajador': result.cod_emp,
                    'nombre_completo': f"{result.nombres} {result.apellidos}",
                    'ci': result.ci,
                    'departamento': result.departamento,
                    'cargo': result.cargo,
                    'unicacion': result.ubicacion,
                    'status': result.status
                }
            return None
    
    
    
    def close(self):
        self.engine.dispose()