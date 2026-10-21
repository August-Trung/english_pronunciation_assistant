"""Scoped assistant actions. Natural-language replies never mutate classroom data."""
from contextlib import closing
import re
import sqlite3
import unicodedata


def normalize(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower().replace('đ', 'd')) if unicodedata.category(c) != 'Mn')


def reply(text, action=None, data=None):
    return {'status': 'success', 'reply': text, 'action': action, 'data': data}


def handle_assistant(message, user, db_path):
    text = normalize(message)
    uid = user['id']
    educator = user.get('role') in ('teacher', 'admin', 'super_admin')
    create = any(w in text for w in ('tao', 'giao', 'create', 'assign ')) and any(w in text for w in ('bai', 'assignment', 'homework'))
    stats = any(w in text for w in ('diem', 'thong ke', 'gradebook', 'analytics', 'hoc sinh yeu'))
    homework = any(w in text for w in ('bai tap', 'han nop', 'chua nop', 'chua lam', 'homework', 'assignment'))
    weak = any(w in text for w in ('tu yeu', 'doc sai', 'phat am sai', 'weak word'))
    with closing(sqlite3.connect(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        if educator and (create or stats or homework or weak):
            # Even administrators only report classes they teach here; no global data fallback.
            classes = conn.execute('SELECT id, name FROM classrooms WHERE teacher_id=? AND COALESCE(IsXoa,0)=0 ORDER BY name', (uid,)).fetchall()
            matching = [c for c in classes if normalize(c['name']) in text or normalize(c['name']).removeprefix('lop hoc ').removeprefix('lop ') in text]
            explicit = re.search(r'\b(?:lop|class)\s+([0-9]+[a-z][a-z0-9]*)', text)
            if explicit:
                matching = [c for c in classes if explicit.group(1) in normalize(c['name'])]
                if not matching:
                    return reply('Mình không tìm thấy lớp ' + explicit.group(1).upper() + ' trong các lớp Thầy/Cô phụ trách. Vui lòng kiểm tra tên lớp.')
            if not classes:
                return reply('Thầy/Cô chưa có lớp đang hoạt động. Hãy tạo lớp trong Teacher Hub trước.')
            chosen = matching[0] if len(matching) == 1 else (classes[0] if len(classes) == 1 and not explicit else None)
            if not chosen:
                return reply('Thầy/Cô muốn xem lớp nào? Các lớp hiện có: ' + ', '.join(c['name'] for c in classes) + '. Vui lòng gửi lại yêu cầu kèm tên lớp.')
            if create:
                return reply('Mình chưa giao bài hay thay đổi dữ liệu. Nhấn Open Teacher Hub, chọn lớp **' + chosen['name'] + '** và Assign Homework để nhập nội dung, xem trước và giao bài.', 'open_teacher', {'class_id': chosen['id']})
            if weak:
                rows = conn.execute("""SELECT w.word,SUM(w.error_count) AS errors FROM weak_words w
                    JOIN class_enrollments e ON e.student_id=w.user_id
                    WHERE e.class_id=? AND COALESCE(e.IsXoa,0)=0 AND COALESCE(w.IsXoa,0)=0
                    GROUP BY LOWER(w.word) ORDER BY errors DESC LIMIT 10""", (chosen['id'],)).fetchall()
                return reply('**Từ cần luyện của lớp ' + chosen['name'] + '**\n\n' + ('\n'.join('- '+r['word']+f" ({r['errors']} lỗi đã ghi nhận)" for r in rows) if rows else 'Chưa có dữ liệu từ yếu của lớp này.'))
            if homework and not stats:
                rows = conn.execute("""SELECT a.title,u.name FROM assignments a
                    JOIN class_enrollments e ON e.class_id=a.class_id JOIN users u ON u.id=e.student_id
                    WHERE a.class_id=? AND COALESCE(a.IsXoa,0)=0 AND COALESCE(a.status,'active')='active'
                    AND COALESCE(e.IsXoa,0)=0 AND COALESCE(u.IsXoa,0)=0
                    AND NOT EXISTS (SELECT 1 FROM submissions s WHERE s.assignment_id=a.id AND s.student_id=u.id AND COALESCE(s.IsXoa,0)=0)
                    ORDER BY a.id,u.name""", (chosen['id'],)).fetchall()
                return reply('**Bài chưa nộp — ' + chosen['name'] + '**\n\n' + ('\n'.join('- '+r['title']+': '+r['name'] for r in rows) if rows else 'Không có bài đang mở nào còn chờ học sinh nộp.'), 'open_teacher')
            rows = conn.execute("""SELECT u.id,u.name,
                COUNT(s.id) AS submissions, AVG(COALESCE(s.score_override,s.score)) AS average
                FROM class_enrollments e JOIN users u ON u.id=e.student_id
                LEFT JOIN submissions s ON s.student_id=u.id AND COALESCE(s.IsXoa,0)=0
                  AND s.assignment_id IN (SELECT id FROM assignments WHERE class_id=? AND COALESCE(IsXoa,0)=0)
                WHERE e.class_id=? AND COALESCE(e.IsXoa,0)=0 AND COALESCE(u.IsXoa,0)=0
                GROUP BY u.id ORDER BY u.name""", (chosen['id'], chosen['id'])).fetchall()
            threshold = re.search(r'(?:duoi|below|under)\s*(\d+(?:[.,]\d+)?)', text)
            limit = float(threshold.group(1).replace(',', '.')) if threshold else (6 if 'yeu' in text else None)
            if limit is not None:
                rows = [r for r in rows if r['average'] is not None and r['average'] < limit]
            summary = ['- **' + r['name'] + '**: ' + (f"{r['average']:.1f}/10" if r['average'] is not None else 'Chưa có điểm') + f" ({r['submissions']} lần nộp)" for r in rows]
            return reply('**Bảng điểm lớp ' + chosen['name'] + '**' + (f' — dưới {limit:g} điểm' if limit is not None else '') + '\n\n' + ('\n'.join(summary) if summary else 'Không có học sinh phù hợp.') + '\n\nĐiểm trung bình tính trên các lần nộp còn hiệu lực của lớp này; ưu tiên điểm giáo viên điều chỉnh.', 'stats_queried')
        if not educator and create and not weak and not any(w in text for w in ('luyen', 'practice', '/θ/', '/ð/')):
            return reply('Bạn có thể tự luyện trong Speaking. Việc giao bài cho lớp dành cho giáo viên; mình chưa tạo hay giao bài nào.', 'open_speaking')
        if not educator and stats:
            row = conn.execute('SELECT COUNT(*), AVG(COALESCE(score_override,score)) FROM submissions WHERE student_id=? AND COALESCE(IsXoa,0)=0', (uid,)).fetchone()
            return reply(f'Bạn có {row[0]} lần nộp.' + (f' Điểm trung bình: {row[1]:.1f}/10.' if row[1] is not None else ' Chưa có điểm bài nộp.') + ' Bạn có thể xem chi tiết từng bài trong Homework.', 'open_homework')
        if not educator and homework and not weak:
            rows = conn.execute("""SELECT DISTINCT a.id,a.title,c.name,a.due_date FROM assignments a
                JOIN classrooms c ON c.id=a.class_id JOIN class_enrollments e ON e.class_id=c.id
                WHERE e.student_id=? AND COALESCE(e.IsXoa,0)=0 AND COALESCE(c.IsXoa,0)=0
                AND COALESCE(a.IsXoa,0)=0 AND COALESCE(a.status,'active')='active'
                AND NOT EXISTS (SELECT 1 FROM submissions s WHERE s.assignment_id=a.id AND s.student_id=? AND COALESCE(s.IsXoa,0)=0)
                ORDER BY CASE WHEN a.due_date IS NULL OR a.due_date='' THEN 1 ELSE 0 END,a.due_date,a.id""", (uid, uid)).fetchall()
            return reply('**Bài tập bạn chưa nộp**\n\n' + ('\n'.join('- **'+r['title']+'** — '+r['name']+'; hạn: '+(r['due_date'] or 'Không có') for r in rows) if rows else 'Bạn không có bài tập đang mở nào chưa nộp.'), 'open_homework')
        if weak:
            rows = conn.execute('SELECT word FROM weak_words WHERE user_id=? AND COALESCE(IsXoa,0)=0 ORDER BY error_count DESC LIMIT 5', (uid,)).fetchall()
            if not rows:
                return reply('Mình chưa tìm thấy dữ liệu từ yếu của bạn. Hãy hoàn thành một bài đọc trong Speaking trước; mình sẽ không dùng dữ liệu của học sinh khác.', 'open_speaking')
            words = [r['word'] for r in rows]
            return reply('Các từ cần luyện của bạn: **'+', '.join(words)+'**. Nhấn Open Speaking để luyện và ghi âm.', 'open_speaking', {'focus_words': words})
    if any(w in text for w in ('dong vai', 'roleplay')):
        return reply('Bạn muốn đóng vai trong tình huống nào: nhà hàng, khách sạn hay trường học? Hãy nêu vai của bạn và vai mình đảm nhận; mình sẽ hội thoại bằng tiếng Anh.')
    if '/θ/' in message or '/ð/' in message or 'am th' in text:
        voiced = '/ð/' in message
        return reply('Với âm **'+('/ð/' if voiced else '/θ/')+'**: đặt nhẹ đầu lưỡi giữa hai răng cửa, thổi hơi nhẹ '+('và rung dây thanh quản. Từ luyện: this, that, mother.' if voiced else 'và không rung dây thanh quản. Từ luyện: think, three, thanks.')+' Đừng cắn chặt lưỡi. Mình chưa nghe bản ghi nên chưa thể kết luận bạn phát âm đúng hay sai.')
    return None
