def get_neighbour(ring, own_ip, direction='left'):
    own_ip_index = ring.index(own_ip) if own_ip in ring else -1 
    if own_ip_index != -1:
        if direction == 'left':
            if own_ip_index + 1 == len(ring):
                return ring[0]
                print("I am the only server and therefore my neighbour")
            else:
                left_neighbour = ring[own_ip_index +1]
                print("My left neighbour is {}".format(left_neighbour))
                right_neighbour = ring[own_ip_index -1]
                print("My right neighbour is {}".format(right_neighbour))
                return left_neighbour, right_neighbour
        else:
            if own_ip_index == 0: 
                return ring[len(ring) - 1]
            else:
                return ring[own_ip_index - 1] 
    else:
        print("Getting neighbour failed.")
        return None
    

members = ("192.168.0.1", "130.234.204.2", "130.234.203.2", "130.234.204.1", "182.4.3.111")

get_neighbour(members, "192.168.0.1", "left")