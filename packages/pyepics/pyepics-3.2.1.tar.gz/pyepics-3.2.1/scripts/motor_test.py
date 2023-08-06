import epics

motorpv = '13IDE:m9'
m1 = epics.Motor(motorpv)

print 'Motor PV=%s   %s ' % (motorpv, m1)
print 'Soft Limits: [low, high] = [% .4f, % .4f] ' % (m1.LLM, m1.HLM)
print '-------------------------------------'

def check_status(motor):
    print 'Motor status for %s' % (motor._prefix)
    print '   Current VAL/Readback = % .4f % .4f' % (motor.VAL, motor.RBV)
    print '   Hard Limits  low, high = %i, %i' % (motor.LLS, motor.HLS)
    print '   Soft Limit Violaton =  %i' % (motor.LVIO)
    try:
        status = motor.check_limits()
        print '   Motor Check_limits() reports OK'
    except:
        print '   Motor Check_limits() reports NOT OK!!'
    print '   '
    
def move_and_check(motor, pos):
    print '-->  move %s to %f' % (motor, pos)
    ret = motor.move(pos, wait=False) # True)
    print 'move return value = %i ' % ( ret)
    check_status(motor)
    
print '### Request Moves within soft limits: '
move_and_check(m1, 5)
# move_and_check(m1, 2)

print '### Request Move outside of limits: '
move_and_check(m1, -3)
move_and_check(m1, -2)

move_and_check(m1, 0)
move_and_check(m1, 0)

print '### Request Move near hard limit'
move_and_check(m1, 0.6)
move_and_check(m1, 0.5)


print '### Request Move past hard limit'
move_and_check(m1, 0.2)
# ;
