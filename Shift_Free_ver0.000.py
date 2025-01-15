import json
from collections import defaultdict

# JSONデータの読み込み
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# コーチの空席数管理
def check_seat_availability(coach_schedule, max_seats):
    return len(coach_schedule) < max_seats

# シフト最適化アルゴリズム（希望講師順を考慮）
def generate_schedule(coaches, students, conditions):
    schedule = defaultdict(list)
    coach_schedules = defaultdict(list)  # 各コーチのスケジュール
    student_sessions = defaultdict(int)  # 各生徒がすでに受けたセッション数

    for student in students:
        for subject, required_sessions in student["required_sessions"].items():
            sessions_scheduled = student_sessions[student["name"]]
            if sessions_scheduled >= required_sessions:
                continue

            # 希望のコーチリストとNGコーチリストを元にスケジュールを割り当て
            available_coaches = [coach for coach in coaches if subject in coach["subjects"]]
            available_coaches = [coach for coach in available_coaches if coach["name"] not in student["ng_coaches"]]

            # 希望するコーチ順に処理
            for preferred_coach in student["preferred_coaches"]:
                coach = next((coach for coach in available_coaches if coach["name"] == preferred_coach), None)
                
                if not coach:
                    continue  # 希望するコーチがいない場合は次の希望に進む
                
                # そのコーチの出勤可能日とコマを調べる
                for date, slots in student["available_schedule"].items():
                    for slot in slots:
                        if sessions_scheduled >= required_sessions:
                            break
                        
                        if date in coach["available_schedule"] and slot in coach["available_schedule"][date]:
                            if check_seat_availability(coach_schedules[coach["name"]], conditions["max_seats"]):
                                # セッションを割り当て
                                coach_schedules[coach["name"]].append({
                                    "student": student["name"],
                                    "subject": subject,
                                    "slot": slot,
                                    "date": date
                                })
                                schedule[date].append({
                                    "student": student["name"],
                                    "coach": coach["name"],
                                    "subject": subject,
                                    "slot": slot
                                })
                                student_sessions[student["name"]] += 1
                                sessions_scheduled += 1
                                break

                    if sessions_scheduled >= required_sessions:
                        break
                if sessions_scheduled >= required_sessions:
                    break
    
    return dict(schedule)

# スケジュールの均等化処理（生徒間のセッション分布を均等にする）
def balance_schedule(schedule, students):
    # 各生徒のセッション数をカウント
    student_sessions = defaultdict(int)
    for date, sessions in schedule.items():
        for session in sessions:
            student_sessions[session["student"]] += 1
    
    # 均等化のための調整（単純な例）
    for student in students:
        for subject, required_sessions in student["required_sessions"].items():
            # この生徒の科目ごとにセッション数を比較
            if student_sessions[student["name"]] < required_sessions:
                # セッションが足りない場合、追加の割り当てを行う（実装例では単純に繰り返し処理）
                pass  # 追加の調整処理をここに書くことができます
    
    return schedule

# メイン処理
def main():
    # JSONファイルのパス
    coaches_file = "coaches.json"
    students_file = "students.json"
    conditions_file = "conditions.json"
    
    # データの読み込み
    coaches = load_json(coaches_file)["coaches"]
    students = load_json(students_file)["students"]
    conditions = load_json(conditions_file)["shift_conditions"]
    
    # スケジュール生成
    schedule = generate_schedule(coaches, students, conditions)
    
    # スケジュール均等化処理
    schedule = balance_schedule(schedule, students)
    
    # 結果を表示
    print("Generated Schedule:")
    for date, sessions in schedule.items():
        print(f"Date: {date}")
        for session in sessions:
            print(f"  {session}")
    
if __name__ == "__main__":
    main()
