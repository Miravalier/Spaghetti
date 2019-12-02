package com.spaghoot.spaghetti.ui.transfer

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProviders
import com.spaghoot.spaghetti.R

class TransferFragment : Fragment() {

    private lateinit var transferViewModel: TransferViewModel

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        transferViewModel =
            ViewModelProviders.of(this).get(TransferViewModel::class.java)
        val root = inflater.inflate(R.layout.fragment_transfer, container, false)

        return root
    }
}