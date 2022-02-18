import logging
from monopoly_simulator import flag_config
from monopoly_simulator.flag_config import flag_config_dict
from monopoly_simulator import bank
logger = logging.getLogger('monopoly_simulator.logging_info.novelty_func')

def alternate_contingency_function_1(player, card, current_gameboard):
    """
    This function has the exact signature as calculate_street_repair_cost.

    Note that this function is being provided as an example. There may be other alternate contingency functions that will
    be written in this file with the exact same syntax but with different logic or values. This function may itself
    undergo changes (but the syntax and function it substitutes will not change).
    :return:
    """
    logger.debug('calculating alternative street repair cost for '+ player.player_name)
    cost_per_house = 70
    cost_per_hotel = 145
    cost = player.num_total_houses * cost_per_house + player.num_total_hotels * cost_per_hotel
    player.charge_player(cost, current_gameboard, bank_flag=True)
    # add to game history
    current_gameboard['history']['function'].append(player.charge_player)
    params = dict()
    params['self'] = player
    params['amount'] = cost
    current_gameboard['history']['param'].append(params)
    current_gameboard['history']['return'].append(None)
    current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

def buy_discount_property(player, asset, current_gameboard):
    """
    Action for player to buy asset from bank. Player must also have enough cash for the asset. Note that if the asset
    does not belong to the bank, the only way currently for player to buy it is if the owner offers to sell it
    and the player accepts the offer.
    :param player: Player instance. The player wants to buy asset
    :param asset: Purchaseable Location instance (railroad, utility or real estate). The asset must currently be owned by the bank
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if player has succeeded in buying the property, failure code if either the player has failed OR if the property ended
    up going to auction (in the latter case, the player may still succeed in obtaining the asset!)
    """
    logger.debug("buy_discount_property function called")
    should_discount = False
    discount_value = 0
    if asset.owned_by != current_gameboard['bank']:
        logger.debug(asset.name+' is not owned by Bank! Resetting option_to_buy for player and returning code failure code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['failure_code']

    if asset.loc_class == "railroad":
        for position in current_gameboard['railroad_positions']:
            if current_gameboard['location_sequence'][position - 1] in player.assets:
                logger.debug("Player has Railroad, so elegible for discount")
                should_discount = True
    if asset.loc_class == "utility":
        for position in current_gameboard['utility_positions']:
            if current_gameboard['location_sequence'][position - 1] in player.assets:
                logger.debug("Player has Utility, so elegible for discount")
                should_discount = True
    if asset.loc_class == "real_estate":
        for a in current_gameboard['color_assets'][asset.color]:
            if a in player.assets:
                logger.debug("Player has asset of the same color, he is elegible for discount")
                should_discount = True

    if should_discount:
        discount_value = 10
    if player.current_cash < asset.price - discount_value:
        asset.price -= discount_value #needs testing??
        # property has to go up for auction.
        index_current_player = current_gameboard['players'].index(player)  # in players, find the index of the current player
        starting_player_index = (index_current_player + 1) % len(current_gameboard['players'])  # the next player's index. this player will start the auction
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' is going up for auction since '+ player.player_name+ ' does not have enough cash to purchase this property. Conducting auction and returning failure code')
        bank.Bank.auction(starting_player_index, current_gameboard, asset)
        # add to game history
        current_gameboard['history']['function'].append(bank.Bank.auction)
        params = dict()
        params['self'] = current_gameboard['bank']
        params['starting_player_index'] = starting_player_index
        params['current_gameboard'] = current_gameboard
        params['asset'] = asset
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['failure_code'] # this is a failure code even though you may still succeed in buying the property at auction
    else:
        logger.debug('Charging '+player.player_name+ ' amount '+str(asset.price)+' for asset '+asset.name)
        player.charge_player(asset.price, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = asset.price
        params['description'] = 'buy property'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        asset.update_asset_owner(player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' ownership has been updated! Resetting option_to_buy for player and returning code successful action code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['successful_action']


def buy_property_right(player, asset, current_gameboard):
    """
    Action for player to buy asset from bank. Player must also have enough cash for the asset. Note that if the asset
    does not belong to the bank, the only way currently for player to buy it is if the owner offers to sell it
    and the player accepts the offer.
    :param player: Player instance. The player wants to buy asset
    :param asset: Purchaseable Location instance (railroad, utility or real estate). The asset must currently be owned by the bank
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if player has succeeded in buying the property, failure code if either the player has failed OR if the property ended
    up going to auction (in the latter case, the player may still succeed in obtaining the asset!)
    """
    if asset.owned_by != current_gameboard['bank']:
        logger.debug(asset.name+' is not owned by Bank! Resetting option_to_buy for player and returning code failure code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['failure_code']

    if asset.start_position != 0:
        left_location = asset.start_position - 1
    else:
        left_location = 39

    if current_gameboard['location_sequence'][left_location].loc_class in ["utility", "railroad", "real_estate"]:
        if current_gameboard['location_sequence'][left_location].owned_by != player:
            logger.debug("Unable to buy property right mayank.")
            return flag_config.flag_config_dict['failure_code']

    logger.debug("Reached left right property after checking")
    if player.current_cash < asset.price:
        # property has to go up for auction.
        index_current_player = current_gameboard['players'].index(player)  # in players, find the index of the current player
        starting_player_index = (index_current_player + 1) % len(current_gameboard['players'])  # the next player's index. this player will start the auction
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' is going up for auction since '+ player.player_name+ ' does not have enough cash to purchase this property. Conducting auction and returning failure code')
        bank.Bank.auction(starting_player_index, current_gameboard, asset)
        # add to game history
        current_gameboard['history']['function'].append(bank.Bank.auction)
        params = dict()
        params['self'] = current_gameboard['bank']
        params['starting_player_index'] = starting_player_index
        params['current_gameboard'] = current_gameboard
        params['asset'] = asset
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['failure_code'] # this is a failure code even though you may still succeed in buying the property at auction
    else:
        logger.debug('Charging '+player.player_name+ ' amount '+str(asset.price)+' for asset '+asset.name)
        player.charge_player(asset.price, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = asset.price
        params['description'] = 'buy property'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        asset.update_asset_owner(player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' ownership has been updated! Resetting option_to_buy for player and returning code successful action code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['successful_action']

def buy_property_rightplayer(player, asset, current_gameboard):
    """
    Action for player to buy asset from bank. Player must also have enough cash for the asset. Note that if the asset
    does not belong to the bank, the only way currently for player to buy it is if the owner offers to sell it
    and the player accepts the offer.
    :param player: Player instance. The player wants to buy asset
    :param asset: Purchaseable Location instance (railroad, utility or real estate). The asset must currently be owned by the bank
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :return: successful action code if player has succeeded in buying the property, failure code if either the player has failed OR if the property ended
    up going to auction (in the latter case, the player may still succeed in obtaining the asset!)
    """
    if asset.owned_by != current_gameboard['bank']:
        logger.debug(asset.name+' is not owned by Bank! Resetting option_to_buy for player and returning code failure code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['failure_code']

    if asset.start_position != 0:
        left_location = asset.start_position - 1
    else:
        left_location = 39

    rightplayerindex = int(player.player_name[len(player.player_name)-1])
    if rightplayerindex == 3:
        rightplayerindex = 0
    else:
        rightplayerindex += 1
    rightplayer = current_gameboard['players'][rightplayerindex]

    if current_gameboard['location_sequence'][left_location].loc_class in ["utility", "railroad", "real_estate"]:
        if current_gameboard['location_sequence'][left_location].owned_by != rightplayer:
            logger.debug("Unable to buy property right sanket.")
            return flag_config.flag_config_dict['failure_code']

    logger.debug("Reached left right propertyrightsanket after checking")
    if player.current_cash < asset.price:
        # property has to go up for auction.
        index_current_player = current_gameboard['players'].index(player)  # in players, find the index of the current player
        starting_player_index = (index_current_player + 1) % len(current_gameboard['players'])  # the next player's index. this player will start the auction
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' is going up for auction since '+ player.player_name+ ' does not have enough cash to purchase this property. Conducting auction and returning failure code')
        bank.Bank.auction(starting_player_index, current_gameboard, asset)
        # add to game history
        current_gameboard['history']['function'].append(bank.Bank.auction)
        params = dict()
        params['self'] = current_gameboard['bank']
        params['starting_player_index'] = starting_player_index
        params['current_gameboard'] = current_gameboard
        params['asset'] = asset
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['failure_code'] # this is a failure code even though you may still succeed in buying the property at auction
    else:
        logger.debug('Charging '+player.player_name+ ' amount '+str(asset.price)+' for asset '+asset.name)
        player.charge_player(asset.price, current_gameboard, bank_flag=True)
        # add to game history
        current_gameboard['history']['function'].append(player.charge_player)
        params = dict()
        params['self'] = player
        params['amount'] = asset.price
        params['description'] = 'buy property'
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        asset.update_asset_owner(player, current_gameboard)
        # add to game history
        current_gameboard['history']['function'].append(asset.update_asset_owner)
        params = dict()
        params['self'] = asset
        params['player'] = player
        params['current_gameboard'] = current_gameboard
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        logger.debug(asset.name+ ' ownership has been updated! Resetting option_to_buy for player and returning code successful action code')
        player.reset_option_to_buy()
        # add to game history
        current_gameboard['history']['function'].append(player.reset_option_to_buy)
        params = dict()
        params['self'] = player
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(None)
        current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

        return flag_config.flag_config_dict['successful_action']

def improvePropertyRed_novelty(player, asset, current_gameboard, add_house=True, add_hotel=False):

    """Novelty: A red property can be improved only after some yellow property has been improved."""
    """
    Function for improving asset belonging to player by adding house or hotel.
    Another thing to remember is that once you add a hotel, it stands as its own unit. If you decide to sell, you'll
    have to sell the entire hotel or not at all.
    :param player: Player instance. The player who is attempting to improve an asset by building houses or hotels.
    :param asset: RealEstateLocation instance.
    :param current_gameboard: A dict. The global data structure representing the current game board.
    :param add_house: A Boolean. True if you want to add a house to asset.
    :param add_hotel: A Boolean. True if you want to add a hotel to asset.
    :return: successful action code if player has successfully managed to improve property or failure code otherwise.
    """
    if asset.owned_by != player or asset.is_mortgaged:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own this property, or it is mortgaged. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.loc_class != 'real_estate':
        logger.debug(asset.name+' is not real estate and cannot be improved. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.color not in player.full_color_sets_possessed:
        # these are the usual conditions that we verify before allowing any improvement to proceed
        logger.debug(player.player_name+' does not own all properties of this color, hence it cannot be improved. Returning failure code')
        return flag_config_dict['failure_code']
    elif player.current_cash <= asset.price_per_house:
        logger.debug(player.player_name+ ' cannot afford this improvement. Returning failure code')
        return flag_config_dict['failure_code']
    elif asset.color == 'Red':
        improveYellowlocation = False
        for yellowproperty in current_gameboard['color_assets']['Yellow']:
            if yellowproperty.num_houses > 0 or yellowproperty.num_hotels > 0:
                improveYellowlocation = True
                break
        if improveYellowlocation == False:
            logger.debug("Novelty: A red property can be improved only after some yellow property has been improved.")
            return flag_config_dict['failure_code']

    if add_hotel: # this is the simpler case
        logger.debug('Looking to improve '+asset.name+' by adding a hotel.')
        if asset.num_hotels == current_gameboard['bank'].hotel_limit:
            logger.debug('There is already ' + str(current_gameboard['bank'].hotel_limit) + ' hotel(s) here. You cannot exceed this limit. Returning failure code')
            return flag_config_dict['failure_code']
        elif asset.num_hotels == 0 and asset.num_houses != current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('You need to have ' + str(current_gameboard['bank'].house_limit_before_hotel)
                         + ' houses before you can build a hotel...Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if asset.num_hotels == 0 and not (same_colored_asset.num_houses == current_gameboard['bank'].house_limit_before_hotel
                    or same_colored_asset.num_hotels == 1): # as long as all other houses
                # of that color have either max limit of houses before hotel can be built or a hotel, we can build a hotel on this asset. (Uniform improvement rule)
                flag = False
                break
            elif same_colored_asset.num_hotels < asset.num_hotels:
                flag = False
                break
        if flag:
            if current_gameboard['bank'].improvement_possible(player, asset, current_gameboard, add_house=False, add_hotel=True):
                logger.debug('Improving asset and updating num_total_hotels and num_total_houses. Currently property has ' + str(asset.num_hotels))
                player.num_total_hotels += 1
                player.num_total_houses -= asset.num_houses
                logger.debug(player.player_name+' now has num_total_hotels '+str(player.num_total_hotels)+' and num_total_houses '+str(player.num_total_houses))
                logger.debug('Charging player for improvements.')
                player.charge_player(asset.price_per_house, current_gameboard, bank_flag=True)
                current_gameboard['bank'].total_hotels -= 1
                current_gameboard['bank'].total_houses += asset.num_houses
                logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house
                params['description'] = 'improvements'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses = 0
                asset.num_hotels += 1
                logger.debug('Player has successfully improved property. Returning successful action code')
                return flag_config_dict['successful_action']

            else:
                logger.debug('Bank has no hotels left for purchase. Kindly wait till someone returns a hotel to the bank.')
                return flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must be uniformly improved first before you can build a hotel on this property. Returning failure code')
            return flag_config_dict['failure_code']

    elif add_house:
        logger.debug('Looking to improve '+asset.name+' by adding a house. Currently property has ' + str(asset.num_houses))
        if asset.num_hotels > 0 or asset.num_houses == current_gameboard['bank'].house_limit_before_hotel:
            logger.debug('There is already a hotel here or you have built the max number of houses that you can on a property. '
                         'You are not permitted another house. Returning failure code')
            return flag_config_dict['failure_code']
        flag = True
        current_asset_num_houses = asset.num_houses
        for same_colored_asset in current_gameboard['color_assets'][asset.color]:
            if same_colored_asset == asset:
                continue
            if same_colored_asset.num_houses < current_asset_num_houses or same_colored_asset.num_hotels > 0:
                flag = False
                break
        if flag:
            if current_gameboard['bank'].improvement_possible(player, asset, current_gameboard, add_house=True, add_hotel=False):
                logger.debug('Improving asset and updating num_total_houses.')
                player.num_total_houses += 1
                logger.debug(player.player_name+ ' now has num_total_hotels '+ str(
                    player.num_total_hotels)+ ' and num_total_houses '+ str(player.num_total_houses))
                logger.debug('Charging player for improvements.')
                player.charge_player(asset.price_per_house, current_gameboard, bank_flag=True)
                current_gameboard['bank'].total_houses -= 1
                logger.debug('Bank now has ' + str(current_gameboard['bank'].total_houses) + ' houses and ' + str(current_gameboard['bank'].total_hotels) + ' hotels left.')
                # add to game history
                current_gameboard['history']['function'].append(player.charge_player)
                params = dict()
                params['self'] = player
                params['amount'] = asset.price_per_house
                params['description'] = 'improvements'
                current_gameboard['history']['param'].append(params)
                current_gameboard['history']['return'].append(None)
                current_gameboard['history']['time_step'].append(current_gameboard['time_step_indicator'])

                logger.debug('Updating houses and hotels on the asset')
                asset.num_houses += 1
                logger.debug('Player has successfully improved property. Returning successful action code')
                return flag_config_dict['successful_action']

            else:
                logger.debug('Bank has no houses left for purchase. Kindly wait till someone returns a house to the bank.')
                return flag_config_dict['failure_code']

        else:
            logger.debug('All same-colored properties must be uniformly improved first before you can build a house on this property. Returning failure code')
            return flag_config_dict['failure_code']

    else:
        #ideally should never reach here, but if it does, then return failure code.
        logger.debug("Didnot succeed in improving house/hotel. Returning failure code.")
        return flag_config_dict['failure_code']