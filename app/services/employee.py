from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Optional, Dict
import os
from dotenv import load_dotenv
import urllib.parse

class EmployeeService:
    def __init__(self):
        load_dotenv()
        
        driver = os.getenv("DRIVER")
        server = os.getenv("SERVER")
        database = os.getenv("DB_NAME")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        
        # URL-encode the password to handle special characters
        encoded_password = urllib.parse.quote_plus(password)
        
        # Create SQLAlchemy engine with ODBC
        connection_string = (
            f"DRIVER={{{driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={encoded_password};"
            f"TrustServerCertificate=yes;"
        )

        # Create ODBC connection string
        self.engine = create_engine(
            f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(connection_string)}",
            pool_pre_ping=True,
            echo=False
        )
        self.Session = sessionmaker(bind=self.engine)
    
    def get_employee_code(self, document_number: str) -> Optional[str]:
        query = text("""
            SELECT
                e.cod_emp
            FROM
                snemple AS e
            WHERE
                e.ci = :document_number
        """)
        
        with self.Session() as session:
            result = session.execute(query, {'document_number': document_number}).fetchone()
            return result[0] if result else None
        
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
                return {
                    'codigo_trabajador': result.cod_emp,
                    'nombre_completo': f"{result.nombres} {result.apellidos}",
                    'ci': result.ci,
                    'departamento': result.departamento,
                    'cargo': result.cargo,
                    'ubicacion': result.ubicacion,
                    'status': result.status
                }
            return None
    
    def close(self):
        self.engine.dispose()