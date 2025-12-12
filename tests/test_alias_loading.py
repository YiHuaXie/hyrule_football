"""测试联赛名称匹配器

验证从 JSON 文件加载联赛别名并测试匹配功能
"""

from hyrule_football.utils.league_matcher import LEAGUE_ALIASES, match_league_name


def test_alias_loading():
    """测试别名映射表加载"""
    print("=" * 60)
    print("测试联赛别名映射表加载")
    print("=" * 60)

    if not LEAGUE_ALIASES:
        print("❌ 别名映射表为空！")
        return

    print(f"\n✅ 成功加载 {len(LEAGUE_ALIASES)} 个联赛别名\n")

    # 显示前 10 个
    print("前 10 个联赛别名：\n")
    for i, (standard_name, aliases) in enumerate(list(LEAGUE_ALIASES.items())[:10], 1):
        print(f"{i:2d}. {standard_name:10s} → {', '.join(aliases)}")

    print("\n" + "=" * 60)


def test_matching():
    """测试匹配功能"""
    print("测试联赛名称匹配")
    print("=" * 60 + "\n")

    test_cases = [
        ("英超", "英超"),
        ("英格兰超级联赛", "英超"),
        ("巴甲", "巴西甲"),
        ("巴西足球甲级联赛", "巴西甲"),
        ("欧冠", "欧冠杯"),
        ("欧洲冠军联赛", "欧冠杯"),
        ("中超", "中超"),
        ("不存在的联赛", None),
    ]

    for input_name, expected in test_cases:
        result = match_league_name(input_name)
        status = "✅" if result == expected else "❌"
        print(
            f"{status} {input_name:20s} → {result or '未找到':15s} (期望: {expected or '未找到'})"
        )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_alias_loading()
    print()
    test_matching()
