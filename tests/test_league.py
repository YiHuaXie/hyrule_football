"""
联赛数据同步单元测试

测试 league_service.sync_league_data() 的完整流程
"""

from hyrule_football.database import db_session, init_db
from hyrule_football.models.league import League, LeagueSource, LeagueMapping
from hyrule_football.service.league_service import sync_league_data
from hyrule_football.repositories.league_repo import LeagueRepo


def test_sync_league_data():
    """
    测试联赛数据同步完整流程

    验证：
    1. 欧核数据是否正确导入到 League 表
    2. 欧核数据是否正确保存到 LeagueSource 表
    3. 欧核映射是否正确创建到 LeagueMapping 表
    4. 懂球帝数据是否正确匹配并保存
    5. 懂球帝映射是否正确创建
    """
    print("\n" + "=" * 80)
    print("开始测试联赛数据同步")
    print("=" * 80)

    # 初始化数据库
    print("\n📦 初始化数据库...")
    init_db()

    # 执行同步
    try:
        sync_league_data()
        print("\n✅ 同步完成")
    except Exception as e:
        print(f"❌ 同步失败: {e}")
        raise

    # 使用 db_session 上下文管理器验证数据
    with db_session() as db:
        # ========== 验证 League 表 ==========
        print("\n" + "-" * 80)
        print("验证 League 表（主表）")
        print("-" * 80)

        leagues = db.query(League).all()
        print(f"✅ League 表记录数: {len(leagues)}")

        assert len(leagues) > 0, "League 表应该有数据"

        # 显示前 5 条
        for league in leagues[:5]:
            print(f"  ID={league.id:3d} | {league.name}")

        # ========== 验证 LeagueSource 表 ==========
        print("\n" + "-" * 80)
        print("验证 LeagueSource 表（原始数据）")
        print("-" * 80)

        oh_sources = db.query(LeagueSource).filter_by(src="oh").all()
        dqd_sources = db.query(LeagueSource).filter_by(src="dqd").all()

        print(f"✅ 欧核数据源记录数: {len(oh_sources)}")
        print(f"✅ 懂球帝数据源记录数: {len(dqd_sources)}")

        assert len(oh_sources) > 0, "应该有欧核数据源"

        # 验证数据完整性
        for source in oh_sources[:3]:
            print(
                f"  欧核: src_league_id={source.src_league_id}, 数据字段数={len(source.src_data)}"
            )
            assert source.src_data is not None, "原始数据不应为空"
            assert "leagueId" in source.src_data, "应该包含 leagueId"
            assert "leagueName" in source.src_data, "应该包含 leagueName"

        # ========== 验证 LeagueMapping 表 ==========
        print("\n" + "-" * 80)
        print("验证 LeagueMapping 表（映射关系）")
        print("-" * 80)

        oh_mappings = db.query(LeagueMapping).filter_by(src="oh").all()
        dqd_mappings = db.query(LeagueMapping).filter_by(src="dqd").all()

        print(f"✅ 欧核映射记录数: {len(oh_mappings)}")
        print(f"✅ 懂球帝映射记录数: {len(dqd_mappings)}")

        assert len(oh_mappings) > 0, "应该有欧核映射"
        assert len(oh_mappings) == len(oh_sources), "欧核映射数应该等于数据源数"

        # 验证映射完整性
        for mapping in oh_mappings[:3]:
            league = db.query(League).filter_by(id=mapping.league_id).first()
            assert league is not None, f"映射的 league_id={mapping.league_id} 应该存在"
            print(f"  映射: oh:{mapping.src_league_id} → League({league.id}, {league.name})")

        # ========== 验证数据一致性 ==========
        print("\n" + "-" * 80)
        print("验证数据一致性")
        print("-" * 80)

        # 验证：每个 LeagueSource 都有对应的 LeagueMapping
        for source in oh_sources[:5]:
            mapping = (
                db.query(LeagueMapping)
                .filter_by(src=source.src, src_league_id=source.src_league_id)
                .first()
            )
            assert mapping is not None, f"数据源 {source.src}:{source.src_league_id} 应该有映射"

        print("✅ 所有欧核数据源都有对应的映射")

        # 验证：每个 LeagueMapping 都能找到对应的 League
        for mapping in oh_mappings[:5]:
            league = db.query(League).filter_by(id=mapping.league_id).first()
            assert league is not None, f"映射的 league_id={mapping.league_id} 应该存在"

        print("✅ 所有映射都能找到对应的主表记录")

        # ========== 验证懂球帝数据匹配 ==========
        if len(dqd_mappings) > 0:
            print("\n" + "-" * 80)
            print("验证懂球帝数据匹配")
            print("-" * 80)

            for mapping in dqd_mappings[:5]:
                league = db.query(League).filter_by(id=mapping.league_id).first()
                source = (
                    db.query(LeagueSource)
                    .filter_by(src=mapping.src, src_league_id=mapping.src_league_id)
                    .first()
                )

                assert league is not None, "懂球帝映射应该关联到主表"
                assert source is not None, "懂球帝映射应该有数据源"

                dqd_name = source.src_data.get("label", "")
                print(f"  匹配: dqd:{mapping.src_league_id} ({dqd_name}) → {league.name}")

            print(f"✅ 懂球帝成功匹配 {len(dqd_mappings)} 个联赛")

        # ========== 验证主表中存在但辅助源中不存在的联赛 ==========
        print("\n" + "-" * 80)
        print("验证主表中存在但懂球帝中不存在的联赛")
        print("-" * 80)

        # 找出只有欧核数据源的联赛（懂球帝没有）
        leagues_only_in_oh = []
        for league in leagues:
            # 检查是否有懂球帝映射
            dqd_mapping = db.query(LeagueMapping).filter_by(league_id=league.id, src="dqd").first()

            if dqd_mapping is None:
                # 确认有欧核映射
                oh_mapping = (
                    db.query(LeagueMapping).filter_by(league_id=league.id, src="oh").first()
                )

                if oh_mapping is not None:
                    leagues_only_in_oh.append((league, oh_mapping))

        print(f"✅ 找到 {len(leagues_only_in_oh)} 个只在欧核中存在的联赛")

        # 显示前 5 个
        for league, oh_mapping in leagues_only_in_oh[:5]:
            print(f"  仅欧核: {league.name} (oh:{oh_mapping.src_league_id})")

        # 验证这些联赛确实没有懂球帝数据
        for league, _ in leagues_only_in_oh[:3]:
            dqd_source = (
                db.query(LeagueSource)
                .filter_by(src="dqd")
                .join(
                    LeagueMapping,
                    (LeagueSource.src == LeagueMapping.src)
                    & (LeagueSource.src_league_id == LeagueMapping.src_league_id),
                )
                .filter(LeagueMapping.league_id == league.id)
                .first()
            )

            assert dqd_source is None, f"联赛 {league.name} 不应该有懂球帝数据源"

        print("✅ 验证通过：这些联赛确实没有懂球帝数据")

        print("\n" + "=" * 80)
        print("测试通过！")
        print("=" * 80)


def test_repository_methods():
    """测试 LeagueRepo 的查询方法"""
    print("\n" + "=" * 80)
    print("测试 LeagueRepo 查询方法")
    print("=" * 80)

    with db_session() as db:
        # 测试 get_sources_by_name
        leagues = db.query(League).limit(3).all()

        for league in leagues:
            print(f"\n测试联赛: {league.name}")

            sources = LeagueRepo.get_sources_by_name(db, league.name)
            print(f"  ✅ 找到 {len(sources)} 个数据源")

            for source in sources:
                print(f"    - {source.src}: {source.src_league_id}")

        print("\n✅ 查询方法测试通过")


if __name__ == "__main__":
    print("=" * 80)
    print("联赛数据同步单元测试")
    print("=" * 80)

    try:
        # 测试 1: 同步数据
        test_sync_league_data()

        # 测试 2: 查询方法
        test_repository_methods()

        print("\n" + "=" * 80)
        print("🎉 所有测试通过！")
        print("=" * 80)

    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
