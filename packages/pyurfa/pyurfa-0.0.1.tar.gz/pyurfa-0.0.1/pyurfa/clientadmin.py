
from client import UrfaClient
from packet import UrfaPacket

class UrfaAdminClient(UrfaClient):

    def rpcf_core_version(self): #0x0045 Работает
        res={}

        if self.urfa_call(0x0045) is False:
            print("Error calling function")
            return False


        packet = self.urfa_get_data()
        res['core_version']=packet.DataGetString()

        return res

    def rpcf_whoami(self): #0x440a Работает
        res={}

        if self.urfa_call(0x440a) is False:
            print("Error calling function")
            return False


        packet = self.urfa_get_data()
        res['my_uid']=packet.DataGetInt()
        res['login']=packet.DataGetString()
        res['user_ip']=packet.DataGetIPAddress()
        res['user_mask']=packet.DataGetIPAddress()

        count=packet.DataGetInt()

        res['system_group_size']=count

        i=0; res['system_groups'] = []; l = {}
        while i < count :
            l['system_group_id']=packet.DataGetInt()
            l['system_group_name']=packet.DataGetString()
            l['system_group_info']=packet.DataGetString()
            res['system_groups'].append(l)
            i += 1


        count=packet.DataGetInt()

        res['allowed_fids_size']=count

        i=0; res['allowed_fids'] = []; l = {}
        while i < count:
            l['id']=packet.DataGetInt()
            l['name']=packet.DataGetString()
            l['module']=packet.DataGetString()
            res['allowed_fids'].append(l)
            i += 1


        count=packet.DataGetInt()

        res['not_allowed_size']=count

        i=0; res['not_allowed_fids'] = []; l={}
        while i < count:
            l['id_not_allowed']=packet.DataGetInt()
            l['name_not_allowed']=packet.DataGetString()
            l['module_not_allowed']=packet.DataGetString()
            res['not_allowed_fids'].append(l)
            i += 1


        return res

    def rpcf_get_houses_list(self): #0x2810 Работает
        res={}

        if self.urfa_call(0x2810) is False:
            print("Error calling function")
            return False

        packet = self.urfa_get_data()

        count = packet.DataGetInt()

        res['count'] = count

        i=0; res['houses'] = []; house = {}
        while i < count:
            house['house_id']=packet.DataGetInt()
            house['ip_zone_id']=packet.DataGetInt()
            house['connect_date']=packet.DataGetInt()
            house['post_code']=packet.DataGetString()
            house['country']=packet.DataGetString()
            house['region']=packet.DataGetString()
            house['city']=packet.DataGetString()
            house['street']=packet.DataGetString()
            house['number']=packet.DataGetString()
            house['building']=packet.DataGetString()
            res['houses'].append(house)
            i += 1

        return res

    def rpcf_get_userinfo(self, user_id): #0x2006 Работает
        res={}

        if self.urfa_call(0x2006) is False:
            print("Error calling function")
            return False

        packet = UrfaPacket(self.socket)

        user_id = int(user_id)
        packet.DataSetInt(user_id)

        self.urfa_send_param(packet)

        packet = self.urfa_get_data()
        user= packet.DataGetInt()

        if user == 0:
            return None
        else:
            res['user_id']= user
            accounts_count = packet.DataGetInt()
            res['accounts_count']= accounts_count

            i=0; res['accounts'] = []; account = {}
            while i < accounts_count:
                account['id']=packet.DataGetInt()
                account['name']=packet.DataGetString()
                res['accounts'].append(account)
                i += 1

            res['login']=packet.DataGetString()
            res['password']=packet.DataGetString()
            res['basic_account']=packet.DataGetInt()
            res['full_name']=packet.DataGetString()
            res['create_date']=packet.DataGetInt()
            res['last_change_date']=packet.DataGetInt()
            res['who_create']=packet.DataGetInt()
            res['who_change']=packet.DataGetInt()
            res['is_juridical']=packet.DataGetInt()
            res['jur_address']=packet.DataGetString()
            res['act_address']=packet.DataGetString()
            res['work_tel']=packet.DataGetString()
            res['home_tel']=packet.DataGetString()
            res['mob_tel']=packet.DataGetString()
            res['web_page']=packet.DataGetString()
            res['icq_number']=packet.DataGetString()
            res['tax_number']=packet.DataGetString()
            res['kpp_number']=packet.DataGetString()
            res['bank_id']=packet.DataGetInt()
            res['bank_account']=packet.DataGetString()
            res['comments']=packet.DataGetString()
            res['personal_manager']=packet.DataGetString()
            res['connect_date']=packet.DataGetInt()
            res['email']=packet.DataGetString()
            res['is_send_invoice']=packet.DataGetInt()
            res['advance_payment']=packet.DataGetInt()
            res['house_id']=packet.DataGetInt()
            res['flat_number']=packet.DataGetString()
            res['entrance']=packet.DataGetString()
            res['floor']=packet.DataGetString()
            res['district']=packet.DataGetString()
            res['building']=packet.DataGetString()
            res['passport']=packet.DataGetString()
            res['parameters_size']=packet.DataGetInt()

            i=0; res['parameters'] = []; parameter = {}
            while i < res['parameters_size']:
                parameter['id']=packet.DataGetInt()
                parameter['value']=packet.DataGetString()
                res['parameters'].append(parameter)

            return res


    def rpcf_search_users_new(self, poles,patterns,sel_type=0): #0x1205 Работает
        
        res = { 'user_data_size' : 0,
                'users' : []}

        if self.urfa_call(0x1205) is False:
            print("Error calling function")
            return False

        packet = UrfaPacket(self.socket)

        packet.DataSetInt(len(poles))

        i=0
        while i < len(poles):
            packet.DataSetInt(poles[i])
            i += 1

        packet.DataSetInt(sel_type)
        pat_count=len(patterns)
        packet.DataSetInt(pat_count)

        i=0
        while i < len(patterns):
            packet.DataSetInt(patterns[i]['what_id'])
            packet.DataSetInt(patterns[i]['criterial_id'])

            if patterns[i]['what_id']==33:
                packet.DataSetInt(patterns[i]['pattern'])
            else:
                packet.DataSetString(patterns[i]['pattern'])
            i += 1

        self.urfa_send_param(packet)

        packet = self.urfa_get_data()

        if packet is False:
        #    print('Packet')
            return False

        res['user_data_size']=packet.DataGetInt()

        i=0; user = {}
        while i < res['user_data_size']:
            user['user_id']=packet.DataGetInt()
            user['login']=packet.DataGetString()
            user['basic_account']=packet.DataGetInt()
            user['full_name']=packet.DataGetString()
            user['is_blocked']=packet.DataGetInt()
            user['balance']=packet.DataGetDouble()
            user['ip_address_size']=packet.DataGetInt()

            j = 0; user['ip_address'] = []
            while j < user['ip_address_size']:
                user['ip_groups_count']=packet.DataGetInt()

                k=0; ip_group = {}
                while k < user['ip_groups_count']:
                    ip_group['type']=packet.DataGetInt()
                    ip_group['ip']=packet.DataGetIPAddress()
                    ip_group['mask']=packet.DataGetIPAddress()
                    user['ip_address'].append(ip_group)
                    k += 1
                j += 1

            j = 0
            while j < len(poles):

                if poles[j]==4: user['discount_period_id']=packet.DataGetInt()
                if poles[j]==6: user['create_date']=packet.DataGetInt()
                if poles[j]==7: user['last_change_date']=packet.DataGetInt()
                if poles[j]==8: user['who_create']=packet.DataGetInt()
                if poles[j]==9: user['who_change']=packet.DataGetInt()
                if poles[j]==10: user['is_juridical']=packet.DataGetInt()
                if poles[j]==11: user['juridical_address']=packet.DataGetString()
                if poles[j]==12: user['actual_address']=packet.DataGetString()
                if poles[j]==13: user['work_telephone']=packet.DataGetString()
                if poles[j]==14: user['home_telephone']=packet.DataGetString()
                if poles[j]==15: user['mobile_telephone']=packet.DataGetString()
                if poles[j]==16: user['web_page']=packet.DataGetString()
                if poles[j]==17: user['icq_number']=packet.DataGetString()
                if poles[j]==18: user['tax_number']=packet.DataGetString()
                if poles[j]==19: user['kpp_number']=packet.DataGetString()
                if poles[j]==21: user['house_id']=packet.DataGetInt()
                if poles[j]==22: user['flat_number']=packet.DataGetString()
                if poles[j]==23: user['entrance']=packet.DataGetString()
                if poles[j]==24: user['floor']=packet.DataGetString()
                if poles[j]==25: user['email']=packet.DataGetString()
                if poles[j]==26: user['passport']=packet.DataGetString()
                if poles[j]==40: user['district']=packet.DataGetString()
                if poles[j]==41: user['building']=packet.DataGetString()
                j += 1

            res['users'].append(user)
            i += 1
        return res

    def rpcf_blocks_report(self, user_id=0, account_id=0, group_id=0, apid=0,
                           time_start=None,
                           time_end=None,
                           show_all=1): # 0x3004
        res={}

        if self.urfa_call(0x3004) is False:
            print("Error calling function")
            return False

        packet = UrfaPacket(self.socket)
        packet.DataSetInt(user_id)
        packet.DataSetInt(account_id)
        packet.DataSetInt(group_id)
        packet.DataSetInt(apid)
        packet.DataSetInt(time_start)
        packet.DataSetInt(time_end)
        packet.DataSetInt(show_all)
    
        self.urfa_send_param(packet)


        packet = self.urfa_get_data()
        if packet is not False:

            res['accounts_count']=packet.DataGetInt()

            i=0; res['account']=[]; account={}
            while i < res['accounts_count']:

                account['atr_size']=packet.DataGetInt()

                j=0; account['blocks_report']=[]; blocks_report={}
                while j < account['atr_size']:
                    blocks_report['account_id']=packet.DataGetInt()
                    blocks_report['login']=packet.DataGetString()
                    blocks_report['start_date']=packet.DataGetInt()
                    blocks_report['expire_date']=packet.DataGetInt()
                    blocks_report['what_blocked']=packet.DataGetInt()
                    blocks_report['block_type']=packet.DataGetInt()
                    blocks_report['comment']=packet.DataGetString()
                    account['blocks_report'].append(blocks_report)
                    j += 1

                res['account'].append(account)
                i += 1

            return res




    def rpcf_get_account_external_id(self, account_id):

        if self.urfa_call(0x2039) is False:
            print("Error calling function")
            return False

        packet = UrfaPacket(self.socket)
        packet.DataSetInt(account_id)

        self.urfa_send_param(packet)

        packet = self.urfa_get_data()

        if packet is not False:
            external_id = packet.DataGetString()
            if external_id == '':
                return None
            else:
                return external_id

    def rpcf_is_account_external_id_used(self, external_id): #0x203a

        if self.urfa_call(0x203a) is False:
            print("Error calling function")
            return False

        packet = UrfaPacket(self.socket)
        packet.DataSetString(external_id)

        self.urfa_send_param(packet)

        packet = self.urfa_get_data()

        if packet is not False:
            return packet.DataGetInt()
        return None