"""真实随机姓名及生日生成器"""
import random

FIRST_NAMES = [
    "James", "Michael", "Robert", "John", "David", "William", "Richard", "Joseph",
    "Thomas", "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
    "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian", "George", "Timothy",
    "Ronald", "Jason", "Edward", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas",
    "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon", "Benjamin",
    "Samuel", "Gregory", "Alexander", "Patrick", "Frank", "Raymond", "Jack", "Dennis",
    "Jerry", "Tyler", "Aaron", "Jose", "Adam", "Nathan", "Henry", "Douglas",
    "Zachary", "Peter", "Kyle", "Walter", "Harold", "Jeremy", "Ethan", "Christian",
    "Keith", "Roger", "Noah", "Gerald", "Carl", "Terry", "Sean", "Austin",
    "Arthur", "Lawrence", "Jesse", "Dylan", "Bryan", "Joe", "Jordan", "Billy",
    "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia",
    "Harper", "Evelyn", "Abigail", "Emily", "Ella", "Elizabeth", "Camila", "Luna",
    "Sofia", "Avery", "Mila", "Aria", "Scarlett", "Penelope", "Layla", "Chloe",
    "Victoria", "Madison", "Eleanor", "Grace", "Nora", "Riley", "Zoey", "Hannah",
    "Hazel", "Lily", "Ellie", "Violet", "Lillian", "Zoe", "Stella", "Aurora",
    "Natalie", "Emilia", "Everly", "Leah", "Aubrey", "Willow", "Addison", "Lucy",
    "Audrey", "Bella", "Claire", "Skylar"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell",
    "Sullivan", "Bell", "Coleman"
]


class NameGenerator:
    """真实英文名字生成器"""

    @classmethod
    def generate(cls):
        """
        生成随机真实英文名字
        
        Returns:
            dict: 包含 first_name, last_name, full_name
        """
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        return {
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"{first_name} {last_name}"
        }


def generate_email(school_domain='psu.edu'):
    """生成随机学校邮箱"""
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    username = ''.join(random.choice(chars) for _ in range(8))
    return f"{username}@{school_domain}"


def generate_birth_date(min_age=19, max_age=23):
    """
    生成大学生合理年龄生日 (19-23岁)
    
    Returns:
        dict: 包含 year, month, day, formatted
    """
    current_year = 2026
    year = current_year - random.randint(min_age, max_age)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    
    return {
        'year': str(year),
        'month': str(month),
        'month_zfill': str(month).zfill(2),
        'day': str(day),
        'day_zfill': str(day).zfill(2),
        'formatted': f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
    }
