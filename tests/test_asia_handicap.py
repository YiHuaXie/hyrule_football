from app.utils import asia_handicap_float


def test_asia_handicap():
    # 从主队角度出发
    #  受让盘，从受20球到受0球 #
    assert asia_handicap_float("受二十球") == 20.0
    assert asia_handicap_float("受二十球/二十球半") == 20.25
    assert asia_handicap_float("受二十球半") == 20.5
    assert asia_handicap_float("受十九球") == 19.0
    assert asia_handicap_float("受十九球/十九球半") == 19.25
    assert asia_handicap_float("受十九球半") == 19.5
    assert asia_handicap_float("受十九球半/二十球") == 19.75

    assert asia_handicap_float("受十八球") == 18.0
    assert asia_handicap_float("受十八球/十八球半") == 18.25
    assert asia_handicap_float("受十八球半") == 18.5
    assert asia_handicap_float("受十八球半/十九球") == 18.75

    assert asia_handicap_float("受十七球") == 17.0
    assert asia_handicap_float("受十七球/十七球半") == 17.25
    assert asia_handicap_float("受十七球半") == 17.5
    assert asia_handicap_float("受十七球半/十八球") == 17.75

    assert asia_handicap_float("受十六球") == 16.0
    assert asia_handicap_float("受十六球/十六球半") == 16.25
    assert asia_handicap_float("受十六球半") == 16.5
    assert asia_handicap_float("受十六球半/十七球") == 16.75

    assert asia_handicap_float("受十五球") == 15.0
    assert asia_handicap_float("受十五球/十五球半") == 15.25
    assert asia_handicap_float("受十五球半") == 15.5
    assert asia_handicap_float("受十五球半/十六球") == 15.75

    assert asia_handicap_float("受十四球") == 14.0
    assert asia_handicap_float("受十四球/十四球半") == 14.25
    assert asia_handicap_float("受十四球半") == 14.5
    assert asia_handicap_float("受十四球半/十五球") == 14.75

    assert asia_handicap_float("受十三球") == 13.0
    assert asia_handicap_float("受十三球/十三球半") == 13.25
    assert asia_handicap_float("受十三球半") == 13.5
    assert asia_handicap_float("受十三球半/十四球") == 13.75

    assert asia_handicap_float("受十二球") == 12.0
    assert asia_handicap_float("受十二球/十二球半") == 12.25
    assert asia_handicap_float("受十二球半") == 12.5
    assert asia_handicap_float("受十二球半/十三球") == 12.75

    assert asia_handicap_float("受十一球") == 11.0
    assert asia_handicap_float("受十一球/十一球半") == 11.25
    assert asia_handicap_float("受十一球半") == 11.5
    assert asia_handicap_float("受十一球半/十二球") == 11.75

    assert asia_handicap_float("受十球") == 10.0
    assert asia_handicap_float("受十球/十球半") == 10.25
    assert asia_handicap_float("受十球半") == 10.5
    assert asia_handicap_float("受十球半/十一球") == 10.75

    assert asia_handicap_float("受九球") == 9.0
    assert asia_handicap_float("受九球/九球半") == 9.25
    assert asia_handicap_float("受九球半") == 9.5
    assert asia_handicap_float("受九球半/十球") == 9.75

    assert asia_handicap_float("受八球") == 8.0
    assert asia_handicap_float("受八球/八球半") == 8.25
    assert asia_handicap_float("受八球半") == 8.5
    assert asia_handicap_float("受八球半/九球") == 8.75

    assert asia_handicap_float("受七球") == 7.0
    assert asia_handicap_float("受七球/七球半") == 7.25
    assert asia_handicap_float("受七球半") == 7.5
    assert asia_handicap_float("受七球半/八球") == 7.75

    assert asia_handicap_float("受六球") == 6.0
    assert asia_handicap_float("受六球/六球半") == 6.25
    assert asia_handicap_float("受六球半") == 6.5
    assert asia_handicap_float("受六球半/七球") == 6.75

    assert asia_handicap_float("受五球") == 5.0
    assert asia_handicap_float("受五球/五球半") == 5.25
    assert asia_handicap_float("受五球半") == 5.5
    assert asia_handicap_float("受五球半/六球") == 5.75

    assert asia_handicap_float("受四球") == 4.0
    assert asia_handicap_float("受四球/四球半") == 4.25
    assert asia_handicap_float("受四球半") == 4.5
    assert asia_handicap_float("受四球半/五球") == 4.75

    assert asia_handicap_float("受三球") == 3.0
    assert asia_handicap_float("受三球/三球半") == 3.25
    assert asia_handicap_float("受三球半") == 3.5
    assert asia_handicap_float("受三球半/四球") == 3.75

    assert asia_handicap_float("受两球") == 2.0
    assert asia_handicap_float("受两球/两球半") == 2.25
    assert asia_handicap_float("受两球半") == 2.5
    assert asia_handicap_float("受两球半/三球") == 2.75

    assert asia_handicap_float("受一球") == 1.0
    assert asia_handicap_float("受一球/一球半") == 1.25
    assert asia_handicap_float("受球半") == 1.5
    assert asia_handicap_float("受一球半/两球") == 1.75

    assert asia_handicap_float("受平手") == 0.0
    assert asia_handicap_float("受平/半") == 0.25
    assert asia_handicap_float("受半球") == 0.5
    assert asia_handicap_float("受半球/一球") == 0.75

    #
    # 正让盘，从0球到20球
    #
    assert asia_handicap_float("平手") == 0.0
    assert asia_handicap_float("平/半") == -0.25
    assert asia_handicap_float("半球") == -0.5
    assert asia_handicap_float("半球/一球") == -0.75

    assert asia_handicap_float("一球") == -1.0
    assert asia_handicap_float("一球/一球半") == -1.25
    assert asia_handicap_float("球半") == -1.5
    assert asia_handicap_float("一球半/两球") == -1.75

    assert asia_handicap_float("两球") == -2.0
    assert asia_handicap_float("两球/两球半") == -2.25
    assert asia_handicap_float("两球半") == -2.5
    assert asia_handicap_float("两球半/三球") == -2.75

    assert asia_handicap_float("三球") == -3.0
    assert asia_handicap_float("三球/三球半") == -3.25
    assert asia_handicap_float("三球半") == -3.5
    assert asia_handicap_float("三球半/四球") == -3.75

    assert asia_handicap_float("四球") == -4.0
    assert asia_handicap_float("四球/四球半") == -4.25
    assert asia_handicap_float("四球半") == -4.5
    assert asia_handicap_float("四球半/五球") == -4.75

    assert asia_handicap_float("五球") == -5.0
    assert asia_handicap_float("五球/五球半") == -5.25
    assert asia_handicap_float("五球半") == -5.5
    assert asia_handicap_float("五球半/六球") == -5.75

    assert asia_handicap_float("六球") == -6.0
    assert asia_handicap_float("六球/六球半") == -6.25
    assert asia_handicap_float("六球半") == -6.5
    assert asia_handicap_float("六球半/七球") == -6.75

    assert asia_handicap_float("七球") == -7.0
    assert asia_handicap_float("七球/七球半") == -7.25
    assert asia_handicap_float("七球半") == -7.5
    assert asia_handicap_float("七球半/八球") == -7.75

    assert asia_handicap_float("八球") == -8.0
    assert asia_handicap_float("八球/八球半") == -8.25
    assert asia_handicap_float("八球半") == -8.5
    assert asia_handicap_float("八球半/九球") == -8.75

    assert asia_handicap_float("九球") == -9.0
    assert asia_handicap_float("九球/九球半") == -9.25
    assert asia_handicap_float("九球半") == -9.5
    assert asia_handicap_float("九球半/十球") == -9.75

    assert asia_handicap_float("十球") == -10.0
    assert asia_handicap_float("十球/十球半") == -10.25
    assert asia_handicap_float("十球半") == -10.5
    assert asia_handicap_float("十球半/十一球") == -10.75

    assert asia_handicap_float("十一球") == -11.0
    assert asia_handicap_float("十一球/十一球半") == -11.25
    assert asia_handicap_float("十一球半") == -11.5
    assert asia_handicap_float("十一球半/十二球") == -11.75

    assert asia_handicap_float("十二球") == -12.0
    assert asia_handicap_float("十二球/十二球半") == -12.25
    assert asia_handicap_float("十二球半") == -12.5
    assert asia_handicap_float("十二球半/十三球") == -12.75

    assert asia_handicap_float("十三球") == -13.0
    assert asia_handicap_float("十三球/十三球半") == -13.25
    assert asia_handicap_float("十三球半") == -13.5
    assert asia_handicap_float("十三球半/十四球") == -13.75

    assert asia_handicap_float("十四球") == -14.0
    assert asia_handicap_float("十四球/十四球半") == -14.25
    assert asia_handicap_float("十四球半") == -14.5
    assert asia_handicap_float("十四球半/十五球") == -14.75

    assert asia_handicap_float("十五球") == -15.0
    assert asia_handicap_float("十五球/十五球半") == -15.25
    assert asia_handicap_float("十五球半") == -15.5
    assert asia_handicap_float("十五球半/十六球") == -15.75

    assert asia_handicap_float("十六球") == -16.0
    assert asia_handicap_float("十六球/十六球半") == -16.25
    assert asia_handicap_float("十六球半") == -16.5
    assert asia_handicap_float("十六球半/十七球") == -16.75

    assert asia_handicap_float("十七球") == -17.0
    assert asia_handicap_float("十七球/十七球半") == -17.25
    assert asia_handicap_float("十七球半") == -17.5
    assert asia_handicap_float("十七球半/十八球") == -17.75

    assert asia_handicap_float("十八球") == -18.0
    assert asia_handicap_float("十八球/十八球半") == -18.25
    assert asia_handicap_float("十八球半") == -18.5
    assert asia_handicap_float("十八球半/十九球") == -18.75

    assert asia_handicap_float("十九球") == -19.0
    assert asia_handicap_float("十九球/十九球半") == -19.25
    assert asia_handicap_float("十九球半") == -19.5
    assert asia_handicap_float("十九球半/二十球") == -19.75

    assert asia_handicap_float("二十球") == -20.0
    assert asia_handicap_float("二十球/二十球半") == -20.25
    assert asia_handicap_float("二十球半") == -20.5
    # assert asia_handicap_float("二十球半/二十一球") == 20.75

    #
    # 特殊写法
    #
    assert asia_handicap_float("平手") == 0.0
    assert asia_handicap_float("平") == 0.0
    assert asia_handicap_float("平半") == -0.25
    assert asia_handicap_float("平/半") == -0.25
    assert asia_handicap_float("半球") == -0.5
    assert asia_handicap_float("半球/一球") == -0.75
    assert asia_handicap_float("球半") == -1.5
    assert asia_handicap_float("受球半") == 1.5
    assert asia_handicap_float("受平半") == 0.25
    assert asia_handicap_float("受平/半") == 0.25


asia_handicap_cases()
