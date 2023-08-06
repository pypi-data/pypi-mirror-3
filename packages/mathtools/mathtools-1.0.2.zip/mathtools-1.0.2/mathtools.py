import math
version = '0.2.1BETA'
class time():
    def second(self,time,_format):
        time = float(time)
        if _format == 'minute':
            return time * 60
        elif _format == 'hour':
            return time * 3600
        elif _format == 'day':
            return time * 3600 * 24
    def hour(self,time,_format):
        time = float(time)
        if _format == 'second':
            return float(time / 3600)
        elif _format == 'minute':
            return float(time / 60)
        elif _format == 'day':
            return float(time * 24)
    def minute(self,time,_format):
        time = float(time)
        if _format == 'second':
            return float(time / 60)
        elif _format == 'hour':
            return float(time * 60)
        elif _format == 'day':
            return float(time * 60 * 24)
    def day(self,time,_format):
        time = float(time)
        if _format == 'second':
            return float(time / 3600 / 24)
        elif _format == 'minute':
            return float(time/60/24)
        elif _format == 'hour':
            return float(time / 24)
class function():
    def graph(self,function,start=[-3,3]):
        results = []
        for x in range(start[0],start[1]+1):
            res = eval(function)
            results.append([x,res])
        return results
class converters():
    def km_miles(self,km):
        return float(km*0.6215)
    def miles_km(self,mi):
        return float(mi*1.609)
    def m_yards(self,m):
        return float(m*1.0936)
    def yards_m(self,y):
        return float(y*0.9144)
    def inch_mm(self,i):
        return float(i*25.4)
    def mm_inch(self,mm):
        return float(mm*0.03937)
    def fahren_celsi(self,f):
        return float((f-32)/(9.0/5.0))
    def celsi_fahren(self,c):
        return float((c*(9.0/5.0))+32)
    def b1(self,n):
        return "01"[n%2]
    def b2(self,n):
        return self.b1(n>>1)+self.b1(n)
    def b3(self,n):
        return self.b2(n>>2)+self.b2(n)
    def b4(self,n):
            return self.b3(n>>4)+self.b3(n)
    def text_binary(self,text):
        bytes = [ self.b4(n) for n in range(256)]
        return ''.join(bytes[ord(c)] for c in text)
class motion():
    def speed(self,distance,time):
        return float(distance)/float(time)
    def time(self,distance,speed):
        return float(distance)/float(speed)
    def distance(self,time,speed):
        return float(time)*float(speed)
    def acceleration(self,v1,v2,t1,t2):
        return float((float(v2)-float(v1))/(float(t2)-float(t1)))
class shapes():
    class square():
        def perimiter(self,w):
            return 4*w
        def area(self,w):
            return w*w
    class cube():
        def volume(self,s):
            return s*s*s
        def area(self,s):
            return (s*s)*6
    class cone():
        def volume(self,b,h,r):
            return (1/3)*math.pi*(r*r)*h
    class rect():
        def perimiter(self,w,h):
            return 2*(w+h)
        def area(self,w,h):
            return w*h
    class circle():
        def perimiter(self,r):
            return 2*math.pi*r
        def area(self,r):
            return math.pi*r*r
    class cylinder():
        def area(self,r,h):
            return math.pi*r*r*h
        def volume(self,r,h):
            return math.pi*r*r*h
    class ellipse():
        def area(self,r1,r2):
            return math.pi*r1*r2
    class sphere():
        def area(r):
            return 4*math.pi*r*r
        def volume(self,r):
            return (4/3)*math.pi*(r*r*r)
    class cone():
        def area(self,r,s):
            return math.pi*r*s
    class rectPrism():
        def volume(self,s1,s2,s3):
            return s1*s2*s3
        def area(self,s1,s2,s3):
            return (2*a*b) + (2*b*c) + (2*a*c)
    class triangle():
        def perimiter(self,a,b,c):
            return a + b +c
class statistics():
    def average(self,numbers,accuracy=3):
        a = len(numbers)
        total = 0.0
        for x in numbers:
            total += x
        return round(total / a,accuracy)
    def percent(self,correct,total):
        return round(float((float(correct)/float(total))*100),2)
