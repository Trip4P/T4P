import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AI.services.popular_service import update_popular_destinations

if __name__ == "__main__":
    update_popular_destinations()