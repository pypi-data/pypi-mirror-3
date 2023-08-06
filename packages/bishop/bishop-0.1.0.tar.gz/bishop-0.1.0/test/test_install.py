import bishop, os

def test_badinstall():
    bad_host = bishop.host.Local(path='test/simple-repo')
    bad_host.roles = ['role4']
    try:
        bad_host.install(path='test/test-install')
        assert False
    except bishop.error.PackageError, e:
        bad_host.unlock()
        return
    assert False

def test_goodinstall():
    good_host = bishop.host.Local(path='test/simple-repo')
    good_host.roles = ['role1', 'role5']
    os.system('rm -rf test/test-install')
    good_host.install(path='test/test-install')
    assert os.path.exists('test/test-install/etc/other_sample.conf')

def test_installdir():
    '''An empty directory should still be created on install (eliminate need of superfluous .empty files)'''
    dir_host = bishop.host.Local(path='test/simple-repo')
    dir_host.roles = ['roledir']
    os.system('rm -rf test/test-install')
    dir_host.install(path='test/test-install')
    assert os.path.exists('test/test-install/etc/empty-dir')

def test_installdir_conflict():
    '''An empty directory that conflicts with a non-empty directory in a separate role should be maintained in the change list but ignored'''
    dirconflict_host = bishop.host.Local(path='test/simple-repo')
    dirconflict_host.roles = ['roledir', 'roleconflictdir']
    os.system('rm -rf test/test-install')
    dirconflict_host.install(path='test/test-install')
    assert os.path.exists('test/test-install/etc/empty-dir/not-empty')

def test_orphan_postinstall():
    '''A postinstall script should be run on its own even if it has no files backing it - instead changes to the script itself will trigger rerun'''
    os.system('rm -rf test/test-install test/simple-repo/.save /tmp/tmp-bishoptest-orphan-postinst')
    postinst_host = bishop.host.Local(path='test/simple-repo')
    postinst_host.roles = ['rolepostinst']
    postinst_host.install(path='test/test-install')
    assert os.path.exists('/tmp/tmp-bishoptest-orphan-postinst')

def test_bishopvars():
    '''A JSON object stored in /etc/bishop-vars.json should be implicitly used to create the context object for templates'''
    bishop.util.vars_path = 'test/simple-repo/test-vars.json'
    bishop.util._tplvars = None
    
    var_host = bishop.host.Local(path='test/simple-repo')
    var_host.roles = ['roletplvars']
    os.system('rm -rf test/test-install')
    var_host.install(path='test/test-install')
    assert os.path.exists('test/test-install/test.txt')
    assert open('test/test-install/test.txt', 'r').read().strip() == 'Message: Hello World!'

    bishop.util.vars_path = '/etc/bishop-vars.json'
    bishop.util._tplvars = None
