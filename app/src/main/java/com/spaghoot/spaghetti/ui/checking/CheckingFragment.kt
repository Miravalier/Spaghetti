package com.spaghoot.spaghetti.ui.checking

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ListView
import androidx.fragment.app.Fragment
import com.spaghoot.spaghetti.R

class CheckingFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val root = inflater.inflate(R.layout.fragment_checking, container, false)

        // Populate account information
        val savingsList: ListView = root.findViewById(R.id.checking_list)
        val adapter = CheckingListAdapter(this.requireContext())
        savingsList.adapter = adapter

        return root
    }
}