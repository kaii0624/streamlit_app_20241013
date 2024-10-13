import streamlit as st
from itertools import combinations

# 名前とエリアの変換辞書
person_names = {
    "Person_1": "田中",
    "Person_2": "佐藤",
    "Person_3": "鈴木",
    "Person_4": "高橋",
    "Person_5": "伊藤",
    "Person_6": "渡辺",
    "Person_7": "山本",
    "Person_8": "中村",
    "Person_9": "小林",
    "Person_10": "加藤",
    "Person_11": "吉田",
    "Person_12": "山田",
    "Person_13": "佐々木",
    "Person_14": "山口",
    "Person_15": "松本",
    "Person_16": "井上",
    "Person_17": "木村",
    "Person_18": "林",
    "Person_19": "斎藤",
    "Person_20": "清水",
    "Person_21": "山崎",
    "Person_22": "森",
    "Person_23": "池田",
    "Person_24": "橋本",
    "Person_25": "石川",
    "Person_26": "前田",
    "Person_27": "藤田",
    "Person_28": "後藤",
    "Person_29": "岡田",
    "Person_30": "長谷川"
}

area_names = {
    "Area_1": "世田谷",
    "Area_2": "渋谷",
    "Area_3": "新宿",
    "Area_4": "港区",
    "Area_5": "中央区",
    "Area_6": "墨田区",
    "Area_7": "豊島区",
    "Area_8": "品川区",
    "Area_9": "目黒区",
    "Area_10": "杉並区",
    "Area_11": "中野区",
    "Area_12": "練馬区",
    "Area_13": "板橋区",
    "Area_14": "足立区",
    "Area_15": "葛飾区",
    "Area_16": "江東区",
    "Area_17": "北区",
    "Area_18": "荒川区",
    "Area_19": "台東区",
    "Area_20": "文京区",
    "Area_21": "中央区",
    "Area_22": "豊島区",
    "Area_23": "品川区",
    "Area_24": "目黒区",
    "Area_25": "世田谷区",
    "Area_26": "港区",
    "Area_27": "新宿区",
    "Area_28": "渋谷区",
    "Area_29": "中野区",
    "Area_30": "杉並区"
}

# 逆変換辞書の作成
name_to_person = {v: k for k, v in person_names.items()}
name_to_area = {}
for k, v in area_names.items():
    if v not in name_to_area:
        name_to_area[v] = []
    name_to_area[v].append(k)

# メイン関数
def main():
    st.title("工事現場差配アプリ")

    st.sidebar.header("設定")

    # チェックボックスによる条件のオンオフ
    preference_condition_on = st.sidebar.checkbox("エリアの好みを考慮する", value=True)
    bad_relationship_condition_on = st.sidebar.checkbox("割り振り禁止ペアを避ける", value=True)
    entertainer_condition_on = st.sidebar.checkbox("現場代理人を配置する", value=True)
    min_area_size_condition_on = st.sidebar.checkbox("エリアごとの最低人数を守る", value=True)

    st.sidebar.markdown("---")

    # 作業員数とエリア数の入力
    num_workers = st.sidebar.number_input("作業員数", min_value=1, value=10, step=1)
    num_areas = st.sidebar.number_input("エリア数", min_value=1, value=3, step=1)

    # エリアリストを作成（内部IDを使用）
    area_list = [f"Area_{i+1}" for i in range(num_areas)]
    display_area_list = [area_names.get(area, area) for area in area_list]

    # 各エリアごとの最低人数の入力
    st.sidebar.subheader("エリアごとの最低人数")
    min_area_sizes = []
    for i in range(num_areas):
        area_display = area_names.get(area_list[i], area_list[i])
        size = st.sidebar.number_input(
            f"{area_display} の最低人数",
            min_value=0,
            value=3,
            step=1,
            key=f"min_size_{i}"
        )
        min_area_sizes.append(size)

    st.sidebar.markdown("---")

    # 割り振り禁止ペアの入力
    st.sidebar.subheader("割り振り禁止ペア")
    bad_pairs_input = st.sidebar.text_area(
        "各行にペアを入力 (例: 田中, 佐藤)",
        value="田中, 佐藤\n鈴木, 高橋"
    )
    bad_pairs = []
    invalid_bad_pairs = False
    for line in bad_pairs_input.strip().split('\n'):
        parts = line.split(',')
        if len(parts) == 2:
            name_a = parts[0].strip()
            name_b = parts[1].strip()
            person_a = name_to_person.get(name_a)
            person_b = name_to_person.get(name_b)
            if person_a and person_b:
                bad_pairs.append((person_a, person_b))
            else:
                invalid_bad_pairs = True
    if invalid_bad_pairs:
        st.sidebar.error("割り振り禁止ペアに無効な名前が含まれています。正しい名前を入力してください。")

    # 現場代理人の入力
    st.sidebar.subheader("現場代理人")
    entertainers_input = st.sidebar.text_input(
        "カンマ区切りで入力 (例: 田中, 佐藤)",
        value="田中, 佐藤, 鈴木, 高橋, 伊藤, 渡辺, 山本, 中村, 小林"
    )
    entertainers = []
    invalid_entertainers = False
    for name in entertainers_input.split(','):
        name = name.strip()
        person_id = name_to_person.get(name)
        if person_id:
            entertainers.append(person_id)
        elif name:
            invalid_entertainers = True
    if invalid_entertainers:
        st.sidebar.error("現場代理人に無効な名前が含まれています。正しい名前を入力してください。")

    st.sidebar.markdown("---")

    # 各作業員のエリアの好みの入力
    st.sidebar.subheader("勤務可能エリア (各作業員ごとに選択)")
    area_preferences = {}
    for i in range(1, num_workers + 1):
        person_id = f'Person_{i}'
        person_display = person_names.get(person_id, person_id)
        prefs = st.sidebar.multiselect(
            f"{person_display} の勤務可能エリア",
            options=display_area_list,
            default=display_area_list,
            key=f"pref_{i}"
        )
        # インデックスに変換
        prefs_indices = []
        for pref in prefs:
            internal_ids = name_to_area.get(pref, [])
            prefs_indices.extend([area_list.index(area_id) for area_id in internal_ids if area_id in area_list])
        area_preferences[person_id] = list(set(prefs_indices)) if prefs_indices else list(range(num_areas))

    st.sidebar.markdown("---")

    # 実行ボタン
    if st.sidebar.button("実行"):
        with st.spinner('割り振りを計算中...'):
            result = assign_areas(
                num_workers=num_workers,
                num_areas=num_areas,
                area_list=area_list,
                min_area_sizes=min_area_sizes,
                bad_pairs=bad_pairs,
                entertainers=entertainers,
                area_preferences=area_preferences,
                preference_condition_on=preference_condition_on,
                bad_relationship_condition_on=bad_relationship_condition_on,
                entertainer_condition_on=entertainer_condition_on,
                min_area_size_condition_on=min_area_size_condition_on
            )

        st.success("計算完了")
        if result['valid']:
            st.markdown("### 最適な割り振り:")
            # エリア数に応じてカラムを生成
            cols = st.columns(num_areas)
            for idx, (area_idx, people) in enumerate(result['assignment'].items()):
                with cols[idx]:
                    area_display = area_names.get(area_list[area_idx], area_list[area_idx])
                    st.subheader(f"{area_display}")
                    if people:
                        for person in people:
                            person_display = person_names.get(person, person)
                            if person in entertainers:
                                person_display += "（現場代理人）"
                            st.write(f"- {person_display}")
                    else:
                        st.write("割り当てなし")
        else:
            st.error("有効な割り振りを見つけることができませんでした。")
        # オプション: 結果の詳細を表示する場合
        # st.text(result['result'])

# エリア割り振り関数
def assign_areas(num_workers, num_areas, area_list, min_area_sizes, bad_pairs, entertainers, area_preferences,
                preference_condition_on, bad_relationship_condition_on,
                entertainer_condition_on, min_area_size_condition_on):

    output_str = ""

    output_str += f"割り振り禁止ペア数: {len(bad_pairs)}\n"
    for pair in bad_pairs:
        name_a = person_names.get(pair[0], pair[0])
        name_b = person_names.get(pair[1], pair[1])
        output_str += f"{name_a} と {name_b} が同じエリアに割り振られないようにします。\n"

    entertainers_display = ", ".join([person_names.get(ent, ent) for ent in entertainers])
    output_str += f"現場代理人: {entertainers_display}\n"

    if min_area_size_condition_on:
        min_area_sizes_display = [str(size) for size in min_area_sizes]
        output_str += f"エリアごとの最低人数: {min_area_sizes_display}\n"

    # 関係行列を生成（割り振り禁止ペアは1、それ以外は0）
    relationship_matrix = [[0 for _ in range(num_workers)] for _ in range(num_workers)]

    for pair in bad_pairs:
        try:
            person_a = int(pair[0].split('_')[1]) - 1  # 0-based index
            person_b = int(pair[1].split('_')[1]) - 1
            relationship_matrix[person_a][person_b] = 1
            relationship_matrix[person_b][person_a] = 1  # 対称性
        except:
            pass  # 無効なペアは無視

    # 部分的な割り振りの有効性を確認する関数
    def is_valid_partial_assignment(area_assignments, relationship_matrix, area_preferences, entertainers, remaining_people):
        for area, people in area_assignments.items():
            # 割り振り禁止ペアが同じエリアにいないか確認
            if bad_relationship_condition_on:
                for person_a, person_b in combinations(people, 2):
                    idx_a = int(person_a.split('_')[1]) - 1
                    idx_b = int(person_b.split('_')[1]) - 1
                    if relationship_matrix[idx_a][idx_b] == 1:
                        return False

            # エリアの好みを守っているか確認
            if preference_condition_on:
                for person in people:
                    area_index = area
                    if area_index not in area_preferences.get(person, []):
                        return False

        # 最低人数の事前チェック
        if min_area_size_condition_on:
            required_people = 0
            for t in range(num_areas):
                current_size = len(area_assignments[t])
                if current_size < min_area_sizes[t]:
                    required_people += (min_area_sizes[t] - current_size)
            if remaining_people < required_people:
                return False

        # 現場代理人の事前チェック
        if entertainer_condition_on:
            # 各エリアに最低1人の現場代理人が配置可能か確認
            for area, people in area_assignments.items():
                if len(people) > 0:
                    has_entertainer = any(person in entertainers for person in people)
                    if not has_entertainer and (remaining_people + len(people)) >= min_area_sizes[area]:
                        pass  # まだ現場代理人を配置できる可能性がある
                else:
                    # エリアが空の場合、少なくとも一人は現場代理人で埋める必要がある
                    pass  # 将来的に現場代理人を配置できるかどうかは後で確認

        return True

    # 完全な割り振りの有効性を確認する関数
    def is_valid_complete_assignment(area_assignments, relationship_matrix, area_preferences, entertainers):
        # エリアごとの最低人数を満たしているか確認
        if min_area_size_condition_on:
            for area in range(num_areas):
                if len(area_assignments[area]) < min_area_sizes[area]:
                    return False

        # 各エリアに少なくとも一人の現場代理人がいるか確認
        if entertainer_condition_on:
            for area in range(num_areas):
                people = area_assignments[area]
                if not any(person in entertainers for person in people):
                    return False

        return True

    # バックトラッキングを用いたエリア割り振り関数
    def backtrack_assign(person_index, area_assignments, relationship_matrix, area_preferences, entertainers, all_assignments):
        nonlocal output_str
        if person_index == num_workers:
            # 全員が割り振られたら、最終的なチェックを行う
            if is_valid_complete_assignment(area_assignments, relationship_matrix, area_preferences, entertainers):
                # 割り振りをコピーして保存
                assignment_copy = {area: people.copy() for area, people in area_assignments.items()}
                all_assignments.append(assignment_copy)
            return

        person = f'Person_{person_index + 1}'
        preferred_areas = area_preferences.get(person, list(range(num_areas)))

        for area in preferred_areas:
            # 現場代理人の条件を考慮
            if entertainer_condition_on:
                # エリアにまだ最低人数に達していない場合、現在の人が現場代理人である必要がある
                if len(area_assignments[area]) < min_area_sizes[area] and person not in entertainers:
                    continue

            # 一時的にエリアに追加
            area_assignments[area].append(person)

            # 残りの人が最低人数を満たすかを事前にチェック
            remaining_people = num_workers - (person_index + 1)
            if not is_valid_partial_assignment(area_assignments, relationship_matrix, area_preferences, entertainers, remaining_people):
                area_assignments[area].remove(person)
                continue

            # 現在の割り振りが有効かチェック（部分的な割り振り用）
            if is_valid_partial_assignment(area_assignments, relationship_matrix, area_preferences, entertainers, remaining_people):
                # 次の人を割り振る
                backtrack_assign(person_index + 1, area_assignments, relationship_matrix, area_preferences, entertainers, all_assignments)
                if all_assignments:
                    return  # 最初の有効な割り振りが見つかったら終了

            # 条件を満たさなければ割り振りを元に戻す
            area_assignments[area].remove(person)

    # バックトラッキングを用いて全ての有効な割り振りを探索する関数
    def assign():
        all_assignments = []
        area_assignments = {i: [] for i in range(num_areas)}
        backtrack_assign(0, area_assignments, relationship_matrix, area_preferences, entertainers, all_assignments)
        return all_assignments

    # 割り振りを実行
    all_area_assignments = assign()

    # 結果を表示
    if all_area_assignments:
        first_assignment = all_area_assignments[0]
        output_str += "最適な割り振り:\n"
        for area in range(num_areas):
            assigned_people = first_assignment[area]
            area_display = area_list[area]
            output_str += f"{area_display}: {', '.join(assigned_people)}\n"
        return {
            "valid": True,
            "assignment": first_assignment,
            "result": output_str
        }
    else:
        output_str += "有効な割り振りを見つけることができませんでした。\n"
        return {
            "valid": False,
            "result": output_str
        }

# アプリケーションの実行
if __name__ == "__main__":
    main()
