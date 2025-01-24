def get_total_progress(self):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Получаем все пробежки участников чата за период челленджа
    cursor.execute("""
        SELECT COALESCE(SUM(r.km), 0)
        FROM running_log r
        WHERE r.date_added BETWEEN ? AND ?
        AND (
            r.chat_id = ?  -- Пробежки, явно привязанные к чату
            OR r.user_id IN (  -- Пробежки участников чата
                SELECT DISTINCT r2.user_id 
                FROM running_log r2 
                WHERE r2.chat_id = ?
            )
        )
    """, (self.start_date, self.end_date, self.chat_id, self.chat_id))
    
    result = cursor.fetchone()
    total_km = result[0] if result else 0
    
    conn.close()
    return total_km 