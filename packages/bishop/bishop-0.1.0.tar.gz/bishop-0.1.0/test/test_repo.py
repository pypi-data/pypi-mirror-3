import bishop
import os, os.path

def test_mirror():
    '''Every node will hold their own repository, but will only mirror the roles necessary to install on the node'''
    master_repo = bishop.repo.Repository(path='test/simple-repo')
    host = bishop.host.Local(path='test/simple-node-repo')
    host.repo = master_repo
    os.system('mkdir -p test/simple-node-repo')
    os.system('rm -rf test/simple-node-repo/*')

    host.mirror(['role1'])
    assert os.path.isdir('test/simple-node-repo/role1')
    assert os.path.exists('test/simple-node-repo/role1/mixins')
    assert os.path.isdir('test/simple-node-repo/role1child')
    assert not os.path.isdir('test/simple-node-repo/role2')
    assert not os.path.isdir('test/simple-node-repo/.build')

def test_build():
    '''Building a repository should create a .build directory in the repository root holding symlinks to all the files to install'''
    host = bishop.host.Local(path='test/simple-repo')
    host.build(['role1', 'role2'])
    assert os.path.isdir('test/simple-repo/.build')
    assert os.path.exists('test/simple-repo/.build/rootfile')
    assert os.path.exists('test/simple-repo/.build/etc/sample.conf')
    assert os.path.exists('test/simple-repo/.build/etc/other_sample.conf')

def test_build_templates():
    host = bishop.host.Local(path='test/simple-repo')
    host.build(['role3'])
    assert os.path.exists('test/simple-repo/.build/etc/templated.conf')
    assert open('test/simple-repo/.build/etc/templated.conf').read().strip() == 'Hello World!'

def test_build_packages():
    host = bishop.host.Local(path='test/simple-repo')
    host.build(['role5'])
    assert open('test/simple-repo/.build/.bishop/packages').read().strip() == 'lynx'

def test_build_prepostinst():
    host = bishop.host.Local(path='test/simple-repo')
    host.build(['role6'])
    assert os.path.exists('test/simple-repo/.build/.bishop/etc/config.conf-postinstall')
    assert not os.path.exists('test/simple-repo/.build/.bishop/etc/config.conf-preinstall')

def test_build_node():
    host = bishop.host.Local(path='test/simple-repo')
    host.roles = ['role2']
    host.build()
    assert os.path.exists('test/simple-repo/.build/etc/sample.conf')

