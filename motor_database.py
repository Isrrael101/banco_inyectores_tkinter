# motor_database.py

class MotorDatabase:
    @staticmethod
    def get_all_motors():
        """Retorna el diccionario completo de todos los motores"""
        return {
            # Motores Cummins
            "Cummins Serie B (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "Cummins ISB 4.5 (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "Cummins ISB 6.7 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Cummins ISC 8.3 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Cummins ISL 8.9 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Cummins ISM 11.0 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Cummins ISX12 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Cummins ISX15 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Cummins QSK19 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Cummins QST30 V12": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),
            "Cummins QSK45 V12": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),
            "Cummins QSK60 V16": (16, "1,16,8,9,3,14,6,11,2,15,7,10,4,13,5,12", "En V"),
            "Cummins QSK78 V18": (18, "1,18,9,10,3,16,7,12,2,17,8,11,4,15,6,13,5,14", "En V"),

            # Motores Caterpillar
            "Caterpillar C4.4 (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "Caterpillar C6.6 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Caterpillar C7 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Caterpillar C9 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Caterpillar C11 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Caterpillar C13 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Caterpillar C15 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Caterpillar C18 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Caterpillar C27 V12": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),
            "Caterpillar C32 V12": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),

            # Motores Detroit Diesel
            "Detroit DD13 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Detroit DD15 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Detroit DD16 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Detroit Series 60 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Detroit 8V-71 (8 cilindros)": (8, "1,5,4,8,6,3,7,2", "En V"),
            "Detroit 12V-71 (12 cilindros)": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),
            "Detroit 16V-71 (16 cilindros)": (16, "1,16,8,9,3,14,6,11,2,15,7,10,4,13,5,12", "En V"),

            # Motores MAN
            "MAN D0834 (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "MAN D0836 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "MAN D2066 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "MAN D2676 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "MAN D2868 (8 cilindros)": (8, "1,5,4,8,6,3,7,2", "En V"),
            "MAN D2840 (10 cilindros)": (10, "1,6,2,7,3,8,4,9,5,10", "En V"),
            "MAN D2842 (12 cilindros)": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),

            # Mercedes-Benz
            "Mercedes-Benz OM 364 (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "Mercedes-Benz OM 366 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Mercedes-Benz OM 444 LA (12 cilindros)": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),
            "Mercedes-Benz OM 460 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Mercedes-Benz OM 502 LA (8 cilindros)": (8, "1,5,4,8,6,3,7,2", "En V"),
            "Mercedes-Benz OM 503 LA (10 cilindros)": (10, "1,6,2,7,3,8,4,9,5,10", "En V"),

            # Scania
            "Scania DC07 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Scania DC09 (5 cilindros)": (5, "1,2,4,5,3", "En Línea"),
            "Scania DC13 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Scania DC16 (8 cilindros)": (8, "1,5,4,8,6,3,7,2", "En V"),

            # Volvo
            "Volvo D5K (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "Volvo D7F (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Volvo D8K (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Volvo D11K (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Volvo D13K (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Volvo D16K (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),

            # MTU
            "MTU 4R (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "MTU 6R (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "MTU 8V (8 cilindros en V)": (8, "1,5,4,8,6,3,7,2", "En V"),
            "MTU 10V 2000 (10 cilindros)": (10, "1,6,2,7,3,8,4,9,5,10", "En V"),
            "MTU 12V 2000 (12 cilindros)": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),
            "MTU 12V 4000 (12 cilindros)": (12, "1,12,5,8,3,10,6,7,2,11,4,9", "En V"),

            # Deutz
            "Deutz TCD 3.6 (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "Deutz TCD 4.1 (4 cilindros)": (4, "1,3,4,2", "En Línea"),
            "Deutz TCD 6.1 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Deutz TCD 7.8 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Deutz TCD 12.0 (6 cilindros)": (6, "1,5,3,6,2,4", "En Línea"),
            "Deutz TCD 16.0 (8 cilindros)": (8, "1,5,4,8,6,3,7,2", "En V")
        }
    