// superfuture.cpp
//
// Author: Thomas Twomey with The BAD group
// Date: 4/10/2020
//
// This is the contract that enables all the functionality for the parking app.
// It also uses actions in the eosio.token contract.
//
// superFuture will contain all the actions for futures, options, spot ledger,
// and groups

#include <eosio/eosio.hpp>
#include <eosio/asset.hpp>
#include <eosio/system.hpp>
#include <eosio/transaction.hpp>

//Hardcoded path
#include "../../eosio.token/include/eosio.token/eosio.token.hpp"

using namespace eosio;

class [[eosio::contract("superfuture")]] superfuture : public eosio::contract {
  private:
    // original future code
    struct [[eosio::table]] half {
      name buyer;
      name seller;
      name initiator; //The person that starts the transation, equalto buyer or seller
      uint16_t sublot_id;
      uint16_t spot_id;
      uint32_t start_time;
      uint32_t end_time;
      uint32_t request_expiration_time;
      asset price;
      uint64_t future_id;

      uint64_t primary_key() const {return future_id;} //We need to change this
      uint64_t get_secondary_1() const {return (sublot_id<<16)+spot_id;}
      uint64_t get_secondary_2() const {return price.amount;} //Need to check type of price.amount
    };

    // The storage for halves of futures, or futures that need to be completed
    typedef eosio::multi_index<name("halves"), half,
      indexed_by<"byspot"_n, const_mem_fun<half, uint64_t, &half::get_secondary_1>>,
      indexed_by<"byprice"_n, const_mem_fun<half, uint64_t, &half::get_secondary_2>>
       > halves_table;

    halves_table _halves;

    // Method to get the current time for checking purposes
    uint32_t now() {
      return current_time_point().sec_since_epoch();
    }

    // Wrapper for a call to the eosio.token tranfer action
    void currency_transfer(name buyer, name seller, asset price)
    {
      action(
        permission_level{buyer,"active"_n},
        "eosio.token"_n,
        "transfer"_n,
        std::make_tuple(buyer, seller, price, std::string("Currency for spot"))
      ).send();
    }

    // Name to all for match of "" in input
    name null_name  = name(0);

//////////////////////////////////////////////////////////////////////////////////////
   // Spotledger code for data storage
//////////////////////////////////////////////////////////////////////////////////////

  // stranfer holds the two halves of a created future
   struct [[eosio::table]] stransfer {
     uint64_t pkey;
     name from;
     name to;
     uint64_t from_group_id;
     uint64_t to_group_id;
     uint16_t sublot_id;
     uint16_t spot_id;
     uint32_t transfer_time; //Time in which the spot changes ownership
     uint32_t creation_time; //Time in which the transfer was agreed upon
     uint64_t future_id;

     uint64_t primary_key() const {return pkey;}
     uint64_t get_secondary() const {return (sublot_id<<16)+spot_id;}
     uint64_t get_future_id() const {return future_id;}
   };

   typedef eosio::multi_index<name("stransfers"), stransfer,
     indexed_by<"byspot"_n, const_mem_fun<stransfer, uint64_t, &stransfer::get_secondary>>,
     indexed_by<"byfuture"_n, const_mem_fun<stransfer, uint64_t, &stransfer::get_future_id>>
     > stransfers_table;

   stransfers_table _stransfers;

   // Struct used to pass an owner and expiration time for the purpsoe or interal
   // ownership chekcing
   struct owner_exp {
     name owner;
     uint32_t expiration_time;
   };
   typedef struct owner_exp own_exp;

 //////////////////////////////////////////////////////////////////////////////////////
    // Options code for data storage
 //////////////////////////////////////////////////////////////////////////////////////

   struct [[eosio::table]] ohalf {
     uint64_t pkey;
     name buyer;
     name seller;
     name caller;
     name putter;
     uint16_t sublot_id;
     //Note that there is no spot_id we are accepting any spot_id
     uint32_t start_time;
     uint32_t end_time;
     uint32_t contract_expiration_time; //The expiration time for the contrat
     uint32_t request_expiration_time; //The contract must be made before this time
     asset spot_price;
     asset contract_price;
     asset collateral;

     uint64_t primary_key() const {return pkey;}
   };

   typedef eosio::multi_index<"ohalves"_n, ohalf > ohalves_table;

   ohalves_table _ohalves;

   struct [[eosio::table]] owhole {
     name buyer;
     name seller;
     name caller;
     name putter;
     name initiator; //The person that starts the transation, equalto buyer or seller
     //std::string lot,
     uint16_t sublot_id;
     //Note that there is no spot_id we are accepting any spot_id
     uint32_t start_time;
     uint32_t end_time; //Times of underlying asset
     uint32_t contract_expiration_time; //The expiration time for the contrat
     asset spot_price;
     asset collateral;
     uint64_t whole_id;

     uint64_t primary_key() const {return whole_id;}
   };

   typedef eosio::multi_index<"owholes"_n, owhole > owholes_table;

   owholes_table _owholes;

   asset get_balance(name owner, symbol sym){
     asset account_balance = token::get_balance("eosio.token"_n, owner, sym.code());
     return account_balance;
   }

 //////////////////////////////////////////////////////////////////////////////////////
    // original groups code
 //////////////////////////////////////////////////////////////////////////////////////

   struct [[eosio::table]] gstruct {
     std::string title;
     name creator;
     asset fee;
     //asset min_price;
     double min_ratio; //People to spots
     uint64_t group_id;
     uint8_t member_count;
     //name members[20]; //Hardcoded 20 MAX_MEMBERS

     uint64_t primary_key() const {return group_id;}
   };

   typedef eosio::multi_index<"gstructs"_n, gstruct > gstructs_table;

   gstructs_table _gstructs;

   struct [[eosio::table]] mstruct {
     uint64_t pkey;
     name member;
     uint64_t group_id;

     uint64_t primary_key() const {return pkey;}
     uint64_t get_group_id() const {return group_id;}
   };

   typedef eosio::multi_index<"mstructs"_n, mstruct,
   indexed_by<"bygroup"_n, const_mem_fun<mstruct, uint64_t, &mstruct::get_group_id>>
   > mstructs_table;

   mstructs_table _mstructs;

  public:

    //Constructor, creates all the data storage
    superfuture(name receiver, name code, datastream<const char*> ds):contract(receiver, code, ds),
     _halves(receiver, receiver.value), _stransfers(receiver, receiver.value),
     _ohalves(receiver, receiver.value), _owholes(receiver, receiver.value),
     _gstructs(receiver, receiver.value),  _mstructs(receiver, receiver.value) {}

     // Action to make a future half
     // Needs a unique future_id
    [[eosio::action]]
    void crtfuture(
      name buyer,
      name seller,
      uint16_t sublot_id,
      uint16_t spot_id,
      const uint32_t start_time,
      const uint32_t end_time,
      const uint32_t request_expiration_time,
      asset price,
      uint64_t future_id
      ){
        name initiator; //The person that starts the transation, equalto buyer or seller
        //Check that the half was created by who it claims created it
        if (buyer != null_name && seller == null_name){
          require_auth(buyer);
          initiator = buyer;
        }
        else if (seller != null_name && buyer == null_name){
          require_auth(seller);
          initiator = seller;
        } else {
          //Break
          check( false, "Invalid buyer or seller.");
        }

        //Check if the fields are valid.
        check(start_time > now(), "Cannot retroactivly sell");
        check(end_time > start_time, "Start time is before end time");
        check(end_time > now(), "End time is in past");
        check(request_expiration_time > now(), "Future half has expired");

        //Unsure if we have to do these or if they will be checked when we call transfer
        check( price.is_valid(), "Invalid currency(This needs to be Tim Bucks)" );
        check( price.amount > 0, "Spots have positive value (rent control)" );


        // Add the future/half to the table
        _halves.emplace(initiator, [&]( auto& row ) {
          row.buyer = buyer;
          row.seller = seller;
          row.initiator = initiator;
          row.spot_id = spot_id;
          row.sublot_id = sublot_id;
          row.start_time = start_time;
          row.end_time = end_time;
          row.request_expiration_time = request_expiration_time;
          row.price = price;
          row.future_id = future_id;
        });
    }

    // Action to complete a future based on the future_id as a key
    // On sucess creates calls tranferspot and deletes the half
    [[eosio::action]]
    void cptfuture(
      name buyer,
      name seller,
      uint16_t sublot_id,
      uint16_t spot_id,
      const uint32_t start_time,
      const uint32_t end_time,
      const uint32_t request_expiration_time,
      asset price,
      uint64_t future_id
      ){
        check(request_expiration_time > now(), "Future half has expired");
        name completer; //The person that started the transation, equalto buyer or seller
        //Check that the half was created by who it claims created it
        if (buyer != null_name && seller == null_name){
          require_auth(buyer);
          completer = buyer;
        }
        else if (seller != null_name && buyer == null_name){
          require_auth(seller);
          completer = seller;
        } else {
          //Break
          check( false, "Invalid buyer or seller.");
        }

        // Make an iterator to look through it
        auto found_spot = _halves.find(future_id);
        if(found_spot == _halves.end()){
          //error
          check(false, "invalid future_id");
        }

        else{
          //Get information from found_spot (seller/buyer)
          if (buyer != null_name){
            seller = found_spot->seller;
          }
          else {
            buyer = found_spot-> buyer;
          }

          //Transfer the assets each direction as a single action thus if one fails they both fail
          currency_transfer(buyer, seller, price);
          transferspot(sublot_id, spot_id, seller, buyer, start_time, end_time, future_id);

          _halves.erase(found_spot);

        }

    }

///////////////////////////////////////////////////////////////////////////////////////////////
    // Spot ledger methods
///////////////////////////////////////////////////////////////////////////////////////////////

    // Internal method that given a sublot, spot, and time returns a who owns it
    // and when their ownership ends.
    own_exp get_owner_exp(uint16_t sublot_id, uint16_t spot_id, uint32_t time){
      //Find the spot and the owner
      auto spot_id_transfer = _stransfers.get_index<"byspot"_n>();
      auto curr_tran = spot_id_transfer.lower_bound((sublot_id<<16)+spot_id);

      name most_recent_to = curr_tran->to;
      uint32_t to_time = 0; //Time that it was tranfered to the "current" owner
      name closest_from = curr_tran->from;
      uint32_t from_time = std::numeric_limits<uint32_t>::max(); //Time that the owner loses ownership

      while (curr_tran != spot_id_transfer.end() && curr_tran->sublot_id == sublot_id && curr_tran->spot_id == spot_id){
        //The if part of this if block may be unnecassy
        if(curr_tran->transfer_time < time){
          //Check for most_recent_to
          if(curr_tran->transfer_time > to_time){
            to_time = curr_tran->transfer_time;
            most_recent_to = curr_tran->to;
          }
        }
        else{
          //Check for slosest_from
          if(curr_tran->transfer_time < from_time){
            from_time = curr_tran->transfer_time;
            closest_from = curr_tran->from;
          }
        }
        curr_tran++;
      }

      //Make a struct to return
      own_exp output{closest_from, from_time};
      return output;
    }

    //Returns spot_id if the user owns a spot in the sublot in the time frame and max if they do not
    uint16_t sublot_in_timeframe(name user, uint16_t sublot_id, uint32_t start_time, uint32_t end_time){
      auto spot_id_transfer = _stransfers.get_index<"byspot"_n>();
      auto curr_tran = spot_id_transfer.lower_bound((sublot_id<<16));

      //get the number of spots in the sublot
      uint16_t max_spot_id = 0;
      while (curr_tran != spot_id_transfer.end() && curr_tran->sublot_id == sublot_id){
        if(curr_tran->spot_id > max_spot_id){
          max_spot_id = curr_tran->spot_id;
        }
        curr_tran++;
      }
      uint16_t i = 0;
      own_exp temp;
      while(i <= max_spot_id){
        temp = get_owner_exp(sublot_id, i, start_time);
        if(temp.owner == user && temp.expiration_time > end_time){
          return i;
        }
        i++;
      }
      return 65535;
    }

    // mechanism for creating "futures" makes two stranfers that represent the
    // to and from transfer of ownership in that case.
    void transferspot(uint16_t sublot_id, uint16_t spot_id, name from, name to,
      uint32_t transfer_time, uint32_t return_time, uint64_t future_id){

      //Check if the fields are valid.
      check(transfer_time > now(), "Cannot retroactivly transfer");
      check(return_time > now(), "End time is in past");

      own_exp temp = get_owner_exp(sublot_id, spot_id, transfer_time);

      //Check to see if the from user has the spot for the whole duration
      check(temp.owner == from, "Tranfering party does not own the spot at the given time.");
      check(temp.expiration_time > return_time, "Tranfering party loses ownership before return time.");

      // Add the "forward" transfer.
      _stransfers.emplace(_self, [&]( auto& row ){
        row.pkey = ((uint64_t)transfer_time<<32) + (((uint32_t)sublot_id)<<16)+spot_id;
        row.from = from;
        row.to = to;
        row.from_group_id = 0;
        row.to_group_id = 0;
        row.sublot_id = sublot_id;
        row.spot_id = spot_id;
        row.transfer_time = transfer_time; //Time in which the spot changes ownership
        row.creation_time = now();
        row.future_id = future_id;
      });

      // Add the "return"  transfer.
      _stransfers.emplace(_self, [&]( auto& row ){
        row.pkey = ((uint64_t)return_time<<32) + (((uint32_t)sublot_id)<<16)+spot_id;
        row.from = to;
        row.to = from;
        row.from_group_id = 0;
        row.to_group_id = 0;
        row.sublot_id = sublot_id;
        row.spot_id = spot_id;
        row.transfer_time = return_time; //Time in which the spot changes ownership
        row.creation_time = now();
        row.future_id = future_id;
      });

    }


    // Action to create the sublots in the begennig by an admin account
   [[eosio::action]]
    void createsublot(uint16_t sublot_id, uint16_t num_spot, name to, uint32_t transfer_time, uint32_t return_time){
      require_auth("to"); //The school
      //check(to == "admin", "Only the admin can create sublots")

      //Check if the fields are valid.
      check(transfer_time > now(), "Cannot retroactivly transfer");
      check(return_time > now(), "End time is in past");

      for (uint16_t i = 0; i < num_spot; i++) {
        cout << ((uint64_t)transfer_time<<32) + (((uint32_t)sublot_id)<<16)+i;
       // Add the "forward" transfer.
       _stransfers.emplace(_self, [&]( auto& row ){
         row.pkey = ((uint64_t)transfer_time<<32) + (((uint32_t)sublot_id)<<16)+i;
         row.to = to;
         row.sublot_id = sublot_id;
         row.spot_id = i;
         row.transfer_time = transfer_time; //Time in which the spot changes ownership
         row.creation_time = now();
       });

       // Add the "return"  transfer.
       _stransfers.emplace(_self, [&]( auto& row ){
         row.pkey = ((uint64_t)return_time<<32) + (((uint32_t)sublot_id)<<16)+i;
         row.from = to;
         row.sublot_id = sublot_id;
         row.spot_id = i;
         row.transfer_time = return_time; //Time in which the spot changes ownership
         row.creation_time = now();
       });
      }

    }

///////////////////////////////////////////////////////////////////////////////////////////////
    // Option methods
///////////////////////////////////////////////////////////////////////////////////////////////

    // Action to create half a future that must be completed
    // Does not specify a spot_id, only cares about a sublot
    [[eosio::action]]
    void crtoption(
      name buyer,
      name seller,
      name caller,
      name putter,
      uint16_t sublot_id,
      uint32_t start_time,
      uint32_t end_time,
      uint32_t contract_expiration_time, //The expiration time for the contrat
      uint32_t request_expiration_time, //The contract must be made before this time
      asset spot_price,
      asset contract_price,
      asset collateral
    ){

      name initiator; //The person that starts the transation, equalto buyer or seller
      //Check that the half was created by who it claims created it
      if (buyer != null_name && seller == null_name){
        require_auth(buyer);
        initiator = buyer;
      }
      else if (seller != null_name && buyer == null_name){
        require_auth(seller);
        initiator = seller;
      } else {
        //Break
        check( false, "Invalid buyer or seller.");
      }

      //Check if the fields are valid.
      check(start_time > now(), "Cannot retroactivly sell");
      check(end_time > start_time, "Start time is before end time");
      check(end_time > now(), "End time is in past");
      check(request_expiration_time > now(), "Future half has expired");

      // Checks to make sure the fields are ok
      check( spot_price.is_valid(), "Invalid currency(This needs to be Tim Bucks)" );
      check( spot_price.amount > 0, "Spots have positive value (rent control)" );
      check( contract_price.is_valid(), "Invalid currency(This needs to be Tim Bucks)" );
      check( contract_price.amount > 0, "Spots have positive value (rent control)" );
      check( collateral.is_valid(), "Invalid currency(This needs to be Tim Bucks)" );
      check( collateral.amount >= 0, "You cannot have negative collateral" );

      //Create the o_half
      _ohalves.emplace(initiator, [&]( auto& row ){
        row.pkey = (((uint64_t)sublot_id)<<32) + contract_expiration_time;
        row.buyer = buyer;
        row.seller = seller;
        row.caller = caller;
        row.putter = putter;
        row.sublot_id = sublot_id;
        row.start_time = start_time;
        row.end_time = end_time;
        row.contract_expiration_time = contract_expiration_time;
        row.request_expiration_time = request_expiration_time;
        row.spot_price = spot_price;
        row.contract_price = contract_price;
        row.collateral = collateral;
      });

    }

    // Action to Complete an existing option half
    // Must specify a unique whole_id
    [[eosio::action]]
    void cptoption(
      name buyer,
      name seller,
      name caller,
      name putter,
      uint16_t sublot_id,
      uint32_t start_time,
      uint32_t end_time,
      uint32_t contract_expiration_time, //The expiration time for the contrat
      uint32_t request_expiration_time, //The contract must be made before this time
      asset price,
      asset contract_price,
      asset collateral,
      uint64_t whole_id
    ){
      // Find that o_half makes the o_whole and deletes the o_half
      uint64_t key = (((uint64_t)sublot_id)<<32) + contract_expiration_time;

      auto temp_iter = _ohalves.find(key);
      if(temp_iter == _ohalves.end()){
        //Not found
        check(false, "Unable to compete, o_half not found");
      }
      else {
        //found
        //Now we need to create the whole
        if (buyer != null_name){
          seller = temp_iter->seller;
        }
        else {
          buyer = temp_iter-> buyer;
        }
        if (caller != null_name){
          putter = temp_iter->putter;
        }
        else {
          caller = temp_iter-> caller;
        }
        //Every other field should be the same

        _owholes.emplace(get_self(), [&]( auto& row ){
          row.buyer = buyer;
          row.seller = seller;
          row.caller = caller;
          row.putter = putter;
          row.sublot_id = sublot_id;
          row.start_time = start_time;
          row.end_time = end_time;
          row.contract_expiration_time = contract_expiration_time;
          row.spot_price = price;
          row.collateral = collateral; //seller comes from the collateral
          row.whole_id = whole_id;
        });

        //currency transfer of collateral to contract
        currency_transfer(seller, _self, collateral); //Unsure if this will work
        //currecny transfer of contract price from buyer to seller of contract
        currency_transfer(buyer, seller, contract_price);
        //erase o_half
        _ohalves.erase(temp_iter);

      }
    }

    // Actio to exercise the call if valid.
    // If the underliying asset can not be traded the collateral is transfered
    // If the contract has expired it is removed and the collateral returned
    [[eosio::action]]
    void exrcall(
      name caller,
      name putter,
      uint64_t whole_id
    ){
      require_auth(caller);
      auto whole_iter = _owholes.find(whole_id);

      if(whole_iter == _owholes.end()){
        //error
        check(false, "invalid whole_id");
      }

      //Only the buyer can exercise
      check(whole_iter->buyer == caller, "Only the buyer can exercise");
      check(whole_iter->caller == caller, "Someone here is wrong");
      check(whole_iter->contract_expiration_time > now(), "Contract has expired");

      //Check that caller has enough currency
      if(get_balance(caller, whole_iter->spot_price.symbol) > whole_iter->spot_price){
        uint16_t spot_id = sublot_in_timeframe(putter, whole_iter->sublot_id, whole_iter->start_time, whole_iter->end_time);
        if(spot_id < 65535){
          //do transaction
          //Transfer price from caller to putter
          currency_transfer(caller, putter, whole_iter->spot_price);
          //Transfer ownership from putter to caller
          transferspot(whole_iter->sublot_id, spot_id, putter, caller, whole_iter->start_time, whole_iter->end_time, whole_id); // future_id from whole_id

        }
        else{
          currency_transfer(_self, whole_iter->buyer, whole_iter->collateral);
        }
      }
      else{
        currency_transfer(_self, whole_iter->seller, whole_iter->collateral);
      }
      _owholes.erase(whole_iter);
    }

    // Action to exercise the put if valid.
    // If the underliying asset can not be traded the collateral is transfered
    // If the contract has expired it is removed and the collateral returned
    [[eosio::action]]
    void exrput(
      name caller,
      name putter,
      uint64_t whole_id
    ){
      require_auth(putter);
      auto whole_iter = _owholes.find(whole_id);

      if(whole_iter == _owholes.end()){
        //error
        check(false, "invalid whole_id");
      }

      //Only the buyer can exercise
      check(whole_iter->buyer == putter, "Only the buyer can exercise");
      check(whole_iter->putter == putter, "Someone here is wrong");
      check(whole_iter->contract_expiration_time > now(), "Contract has expired");

      //Check that caller has enough currency
      if(get_balance(putter, whole_iter->spot_price.symbol) > whole_iter->spot_price){
        uint16_t spot_id = sublot_in_timeframe(caller, whole_iter->sublot_id, whole_iter->start_time, whole_iter->end_time);
        if(spot_id < 65535){
          //do transaction
          //Transfer price from caller to putter
          currency_transfer(caller, putter, whole_iter->spot_price);
          //Transfer ownership from putter to caller
          transferspot(whole_iter->sublot_id, spot_id, putter, caller, whole_iter->start_time, whole_iter->end_time, whole_id); // future_id from whole_id
        }
        else{
          currency_transfer(_self, whole_iter->buyer, whole_iter->collateral);
        }
      }
      else{
        currency_transfer(_self, whole_iter->seller, whole_iter->collateral);
      }
      _owholes.erase(whole_iter);
    }

    // Action for seller of contract to claim back collateral after contract
    // expires without being exercised
    [[eosio::action]]
    void clmcollat(
      name seller,
      uint64_t whole_id
    ){
      require_auth(seller);
      auto whole_iter = _owholes.find(whole_id);

      if(whole_iter == _owholes.end()){
        //error
        check(false, "invalid whole_id");
      }

      check(whole_iter->seller == seller, "Only the buyer can exercise");
      check(whole_iter->contract_expiration_time < now(), "Contract is still active");

      currency_transfer(_self, seller, whole_iter->collateral);
      _owholes.erase(whole_iter);

    }

  //////////////////////////////////////////////////////////////////////////////////////
     // Groups code
  //////////////////////////////////////////////////////////////////////////////////////

  // Action to create a group, needs a unique group_id
  // With the model we adopted we were unable to implement the min_price or
  // min_ratio functionality.
  [[eosio::action]]
  void crtgroup(
    std::string title,
    name creator,
    asset fee,
    //asset min_price,
    double min_ratio,
    uint64_t group_id
  ){
    require_auth(creator);
    //Sanity checks
    check(fee.amount >= 0, "No negatives");
    check(min_ratio >= 0, "No negatives");
    //Add a row to the muti_index
    _gstructs.emplace(_self,  [&]( auto& row ){
      row.title = title;
      row.creator = creator;
      row.fee = fee;
      row.min_ratio = min_ratio; // Not used
      row.group_id = group_id;
      row.member_count = 0;
    });
  }

  [[eosio::action]]
  void joingroup(name user, uint64_t group_id){
    require_auth(user);

    auto group_itr = _gstructs.find(group_id);
    if(group_itr == _gstructs.end()){
      //Not found
      check(false, "Inavlaid group_id");
    }
    else{
      //Do other checks
      //Transfer
      currency_transfer( user, group_itr->creator, group_itr->fee);
      _gstructs.modify(group_itr, get_self(),  [&]( auto& row ) {
        row.member_count = row.member_count +1;
      });
      _mstructs.emplace(get_self(), [&]( auto& row ){
        row.pkey = _mstructs.available_primary_key();
        row.member = user;
        row.group_id = group_id;
      });
    }
  }


  // Action that gives a future to a group
  [[eosio::action]]
  void ftrtogrp(name owner, uint64_t group_id, uint64_t future_id){
    require_auth(owner);

    auto group_itr = _gstructs.find(group_id);
    if(group_itr == _gstructs.end()){
      //Not found
      check(false, "Inavlaid group_id");
    }
    else{
      //Do other checks
      check(group_itr->creator == owner, "You are not the owner of the group");

      //Find the future(two stransfers)
      //Find the spot and the owner
      auto spot_id_transfer = _stransfers.get_index<"byfuture"_n>();
      auto curr_tran = spot_id_transfer.lower_bound(future_id);

      auto prev_tran = curr_tran;
      curr_tran++;

      check(prev_tran->future_id == future_id, "Future id error.");
      check((curr_tran)->future_id == future_id, "Future id error on second.");

      if (prev_tran->from == owner && (curr_tran)->to == owner) {
        //Update
        spot_id_transfer.modify(prev_tran, get_self(),  [&]( auto& row ) {
          row.from_group_id = group_id;
        });
        spot_id_transfer.modify(curr_tran, get_self(),  [&]( auto& row ) {
          row.to_group_id = group_id;
        });
      } else if (prev_tran->to == owner && (curr_tran)->from == owner) {
        //Update
        spot_id_transfer.modify(prev_tran, get_self(),  [&]( auto& row ) {
          row.to_group_id = group_id;
        });
        spot_id_transfer.modify(curr_tran, get_self(),  [&]( auto& row ) {
          row.from_group_id = group_id;
        });
      } else {
        //Error
        check(false, "Owner of group is not owner of future");
      }

    }

  }

  // Action that removes a future from a group
  [[eosio::action]]
  void ftrfrmgrp(name owner, uint64_t group_id, uint64_t future_id){
    require_auth(owner);

    auto group_itr = _gstructs.find(group_id);
    if(group_itr == _gstructs.end()){
      //Not found
      check(false, "Inavlaid group_id");
    }
    else{
      //Do other checks
      check(group_itr->creator == owner, "You are not the owner of the group");

      //Find the future(two stransfers)
      //Find the spot and the owner
      auto spot_id_transfer = _stransfers.get_index<"byfuture"_n>();
      auto curr_tran = spot_id_transfer.lower_bound(future_id);

      auto prev_tran = curr_tran;
      curr_tran++;

      check(prev_tran->future_id == future_id, "Future id error.");
      check((curr_tran)->future_id == future_id, "Future id error on second.");

      if (prev_tran->from == owner && (curr_tran)->to == owner) {
        //Update
        spot_id_transfer.modify(prev_tran, get_self(),  [&]( auto& row ) {
          row.from_group_id = 0;
        });
        spot_id_transfer.modify(curr_tran, get_self(),  [&]( auto& row ) {
          row.to_group_id = 0;
        });
      } else if (prev_tran->to == owner && (curr_tran)->from == owner) {
        //Update
        spot_id_transfer.modify(prev_tran, get_self(),  [&]( auto& row ) {
          row.to_group_id = 0;
        });
        spot_id_transfer.modify(curr_tran, get_self(),  [&]( auto& row ) {
          row.from_group_id = 0;
        });
      } else {
        //Error
        check(false, "Owner of group is not owner of future");
      }
    }
  }

};
