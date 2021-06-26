# -*- coding: utf-8 -*-
import os
import time
import json

# 需要配置的内容 👇🏻

# 项目配置
project_path = '~/Desktop/HeteClient/HeteClient'  # 项目根目录
daily_build_path = '~/Desktop/HeteClient/DailyBuild'  # 打包后ipa存储目录 请指向自动打包脚本所在目录
project_name = 'HeteClient'  # 工程名
scheme = 'HeteClient'  # scheme
product_name = 'HeteClient'  # 产品名，看工程的Products文件夹里面的名字
project_type = '-workspace'  # 工程类型 -workspace or -project
configuration = 'DailyBuild'  # 编译模式 Debug or Release
destination = "generic/platform=iOS" # M1 Build
# signing_certificate = 'Apple\ Distribution:\ Bowen\ Li'  # 证书名称
# mobileprovision_uuid = 'afe2ae42-f17f-4ab3-baa7-5c5e2cc7f20e'  # mobileprovision_uuid

# pgyer配置
pgyer_apiKey = 'df87486c96920bf5650fa74afc621be3'
pgyer_buildInstallType = 2  # 应用安装方式，2 - 密码安装，3 - 邀请安装
pgyer_buildPassword = '123456'  # 设置app安装密码


# 需要配置的内容 👆🏻


# 打包开始
def daily_build_start():
    print('\n')
    print('** 打包开始 **')
    print('\n')


# Clean
def clean_project():
    os.system('cd %s;xcodebuild clean' % project_path)  # clean项目


# Build
def build_project():
    os.system('cd %s;mkdir build' % project_path)
    if project_type == '-workspace':
        project_suffix_name = 'xcworkspace'
    else:
        project_suffix_name = 'xcodeproj'
    os.system(
        'cd %s;xcodebuild archive %s %s.%s\
        -scheme %s\
        -configuration %s\
        -destination %s\
        -archivePath %s/build/%s\
        ||\
        exit' % (
            project_path,
            project_type,
            project_name,
            project_suffix_name,
            scheme,
            configuration,
            destination,
            project_path,
            project_name
        )
    )
    # os.system(
    #     'cd %s;xcodebuild archive %s %s.%s\
    #     -scheme %s\
    #     -configuration %s\
    #     -destination %s\
    #     -archivePath %s/build/%s\
    #     CODE_SIGN_IDENTITY=%s\
    #     PROVISIONING_PROFILE=%s\
    #     || exit' % (
    #         project_path,
    #         project_type,
    #         project_name,
    #         project_suffix_name,
    #         scheme, 
    #         configuration,
    #         destination,
    #         project_path,
    #         project_name,
    #         signing_certificate,
    #         mobileprovision_uuid
    #     )
    # )


# Export
def export_ipa():
    # noinspection PyGlobalUndefined
    global ipa_filename
    ipa_filename = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    ipa_filename = project_name + '_' + ipa_filename
    os.system(
        '%s/xcodebuild-safe.sh\
        -exportArchive\
        -archivePath %s/build/%s.xcarchive\
        -exportPath %s/%s\
        -exportOptionsPlist %s/exportOptionsPlist.plist' % (
            daily_build_path,
            project_path,
            project_name,
            daily_build_path,
            ipa_filename,
            daily_build_path
        )
    )


# 删除build目录
def remove_project_build():
    os.system('rm -r %s/build' % project_path)


# 上传pgyer
def upload_pgyer():
    local_path_filename = os.path.expanduser(daily_build_path)  # 相对路径转换绝对路径
    if os.path.exists('%s/%s' % (local_path_filename, ipa_filename)):
        print_ipa_info()
        print('** 正在上传蒲公英，请耐心等候... **')
        print('\n')
        file_path = '%s/%s/%s.ipa' % (local_path_filename, ipa_filename, product_name)
        json_str = os.popen(
            'curl\
            -F "_api_key=%s"\
            -F "file=@%s"\
            -F "buildInstallType=%s"\
            -F "buildPassword=%s"\
            https://www.pgyer.com/apiv2/app/upload' % (
                pgyer_apiKey,
                file_path,
                pgyer_buildInstallType,
                pgyer_buildPassword
            )
        ).read()
        print('\n')
        print(json_str)
        print('\n')
        if type(json_str) is str:
            result = json.loads(json_str)
            if isinstance(result, dict) is False \
                    or 'code' not in result.keys() \
                    or (result['code'] != 0 and result['code'] != '0'):
                print('** 上传蒲公英失败 **')
            else:
                print('** 上传蒲公英成功 **')
                remove_ipa()
        else:
            print('** 上传蒲公英失败 **')
    else:
        print('没有找到ipa文件')


# 输出ipa包信息
def print_ipa_info():
    print('\n')
    local_path_filename = os.path.expanduser(daily_build_path)  # 相对路径转换绝对路径
    print('ipa路径为: %s/%s/%s.ipa' % (local_path_filename, ipa_filename, product_name))
    print('\n')


# 删除ipa包
def remove_ipa():
    print('\n')
    local_path_filename = os.path.expanduser(daily_build_path)  # 相对路径转换绝对路径
    os.system('rm -r %s/%s' % (local_path_filename, ipa_filename))  # 这里千万不要删错了
    print('删除路径 %s/%s 成功' % (local_path_filename, ipa_filename))


# 打包结束
def daily_build_end():
    print('\n')
    print('** 打包结束 **')
    print('\n')


def main():
    # 打包开始
    daily_build_start()
    # 清理项目
    clean_project()
    # 构建项目
    build_project()
    # 导出ipa
    export_ipa()
    # 删除build目录
    remove_project_build()
    # 上传pgyer
    upload_pgyer()
    # 打包结束
    daily_build_end()


# 执行
main()
